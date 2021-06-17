import os.path

def ask_for_participant_id():
    id = input('Provide participant ID: ')
    check_participant_id(id)
    return id

def check_participant_id(id):
    if id == "":
        raise Exception('No participant ID provided')
    elif not os.path.isdir('../inputs/{}'.format(id)):
        raise Exception('Input folder for participant {} not found'.format(id))
