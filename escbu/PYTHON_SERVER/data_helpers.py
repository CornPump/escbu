State ={

    # no RAM or DB data management
    'FF':0,
    # use RAM management but no DB data management
    'TF':1,
    # use DB data management but no RAM management
    'FT':2,
    # use RAM and DB data management
    'TT':3
}

clients_keys = ('ID','Name','Public_key','Last_seen','AES_key')
files_keys = ('ID','Name','Path_name','Verified')