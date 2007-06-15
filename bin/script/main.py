if __name__=="__main__":
    from Expression import *
    from modify import *
    from Repeatln import *
    from Fields import *
    import sys

    if sys.argv.__len__()==1:
        ErrorDialog("Enter Proper Argument\nUsage: python main.py commandlineArgs","It must be RepeatIn, Fields, Expression, or Modify")
    else:
        if sys.argv[1]=="RepeatIn":
            RepeatIn()
        elif sys.argv[1]=="Fields":
            Fields()
        elif sys.argv[1]=="Expression":
            Expression()
        elif sys.argv[1]=="Modify":
            modify()
        else:
            ErrorDialog("Enter Proper Argument","It must be RepeatIn, Fields, Expression, or Modify")