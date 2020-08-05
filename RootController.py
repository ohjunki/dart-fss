import MainFlow
import pickle
import FilePathManager as fm

f = open( "{:s}/oneMoreCompany.pkl".format( fm.sharedDirectory ) , "rb" )
oneMoreCompany = pickle.load( f )
f.close()

MainFlow.startDartAnalytics( oneMoreCompany , '073110')  # 192820이거부터 다시하기


