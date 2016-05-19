# this is a little script to simplify managing the database
import heatmap, argparse, os


def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-c", "--command", help="db command to run. options are: 'init', \
                                                 'convert_csv', 'create_index', 'update_from_csv'")
    parser.add_argument("-f", "--file", help="optional csv file to convert. \
                                              uses CSV in config file if not provided")
    parser.add_argument("-i", "--index", help="optional name of index for creating an index. \
                                               uses DB_INDEX in config file if not provided")
    parser.add_argument("-c1", "--column1", help="first database column for creating an index")
    parser.add_argument("-c2", "--column2", help="second database column for creating an index")
    parser.add_argument("-k", "--keep", help="keep the old database as <file>")


    args = parser.parse_args()

    # do commands
    if args.command:
        c = args.command.lower()
        
        if c == 'init':
            heatmap.init_db()
        
        elif c == 'convert_csv':
            if args.file and args.table:
                heatmap.csv_to_table(args.file, args.table)
            elif args.file and not args.table:
                heatmap.csv_to_table(args.file)
            else:
                heatmap.csv_to_table()
                
        elif c == 'create_index':
            if args.index:
                heatmap.create_table_index(args.column1, args.column2, args.index)
            else:
                heatmap.create_table_index(args.column1, args.column2)
                
        elif c == 'update_from_csv':
            if args.file:
                update_from_csv(args.file)
            else:
                update_from_csv()
                    
        else:
            parser.print_help()
    else:
        parser.print_help()


# create a new database then swap it in for the old one
def update_from_csv(csv_file=None, column1='latitude', column2='longitude'):
    database = heatmap.get_default_db()
    database_tmp = database + '.tmp'
    database_old = database + '.old'
    
    # create new db file
    print 'creating new database from file'
    heatmap.init_db(database=database_tmp)
    if csv_file is None:
        heatmap.csv_to_table(database=database_tmp)
    else:
        heatmap.csv_to_table(csv_file=csv_file, database=database_tmp)
    heatmap.create_table_index(column1, column2, database=database_tmp)
    
    # swap databases
    print 'replacing old database'
    os.rename(database,database_old)
    os.rename(database_tmp,database)
    
    # validate new database and remove old
    print 'validating operation was successful'
    if heatmap.table_exists(heatmap.get_default_table()):
        delete_file(database_old)
        print 'operation success'
        return
    # undo operation
    else:
        print 'operation failed'
        delete_file(database)
        os.rename(datase_old, database)
        print 'original database rolled back'
        return


# deletes a file from the system    
def delete_file(filename):
    if os.path.isfile(filename):
        os.remove(filename)
        

if __name__=="__main__":
   main()
