def file_handler_v2(command):
    match command.split():
        case ['show']:
            print('List all files and directories: ')
            # static to list files
        case ['remove' | 'delete', *files] if '--ask' in files:
            del_files = [f for f in files if len(f.split('.'))>1]
            print('Please confirm: Removing files: {}'.format(del_files))
            # static to accept user input, then remove files
        case ['remove' | 'delete', *files]:
            print('Removing files: {}'.format(files))
            # static to remove files
        case _:
            print('Command not recognized')
