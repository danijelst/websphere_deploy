# the call from the console
# wsadmin -f deploy_ear.py PM1 your.ear NodeName ServerName default_host
# http://www.programmingforliving.com/2013/04/was85-application-deployment-using.html

def getOptions(cellName, appInfo, ctxRoot = None):
    options = [ '-preCompileJSPs',
                '-distributeApp',
                '-nouseMetaDataFromBinary',
                '-nodeployejb',
                '-appname', appInfo["appName"],
                '-createMBeansForResources',
                '-noreloadEnabled',
                '-nodeployws',
                '-validateinstall', 'warn',
                '-noprocessEmbeddedConfig',
                '-filepermission .*\.dll=755#.*\.so=755#.*\.a=755#.*\.sl=755',
                '-noallowDispatchRemoteInclude',
                '-noallowServiceRemoteInclude',
                '-asyncRequestDispatchType', 'DISABLED',
                '-nouseAutoLink',
                '-noenableClientModule',
                '-clientMode', 'isolated',
                '-novalidateSchema',
                '-MapWebModToVH', [['pm1j.war', 'pm1j.war,WEB-INF/web.xml', appInfo["virtualHost"]]]
            ]
    if ctxRoot != None:
        options.append('-contextroot')
        options.append(ctxRoot)
    return options
 
def isAppExists(appName):
    return len(AdminConfig.getid("/Deployment:" + appName + "/" )) > 0

def getAppStatus(appName):
    # If objectName is blank, then the application is not running.
    objectName = AdminControl.completeObjectName('type=Application,name=' + appName + ',*')
    if objectName == "":
        appStatus = 'Stopped'
    else:
        appStatus = 'Running'
    return appStatus

def stopApp(nodeName, serverName, appName):
    try:
        if getAppStatus(appName) == 'Running':
            print 'Stopping Application "%s" on "%s/%s"...' %(appName, nodeName, serverName)
            appMgr = AdminControl.queryNames("type=ApplicationManager,node="+nodeName+",process="+serverName+",*" )
            AdminControl.invoke(appMgr, 'stopApplication', appName)
            print 'Application "%s" stopped on "%s/%s"!' %(appName, nodeName, serverName)
        else:
            print 'Application "%s" already stopped on "%s/%s"!' %(appName, nodeName, serverName)
    except:
        print("Ignoring error - %s" % sys.exc_info())
 
def startApp(nodeName, serverName, appName):
    print 'Starting Application "%s" on "%s/%s"...' %(appName, nodeName, serverName)
    appMgr = AdminControl.queryNames("type=ApplicationManager,node="+nodeName+",process="+serverName+",*" )
    AdminControl.invoke(appMgr, 'startApplication', appName)
    print 'Application "%s" started "%s" on "%s/%s"!' %(appName, nodeName, serverName)
 
def removeApp(appName):
    print 'Removing Application "%s"...' %(appName)
    AdminApp.uninstall(appName)
    print 'Application "%s" removed successfully!' %(appName)

def installApp(location, options):
    print 'Installing application from "%s" ...' %(location)
    AdminApp.install(location, options)
    print 'Successfully installed application "%s"' %(location)

def save():
    print 'Saving the changes...'
    AdminConfig.save()
    print 'Changes saved successfully.'

if __name__ == '__main__':   
    if len(sys.argv) < 4:
        print 'ERROR: Not enough information to execute this script'
        print 'deploy.py app_name ear_file_path node_name server_name virtual_host'
        exit()
        
    print 'Initializing...'
    cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
    appInfo = { "appName"    : sys.argv[0],
                "filePath"   : sys.argv[1],
                "nodeName"   : sys.argv[2],
                "serverName" : sys.argv[3],
                "virtualHost": sys.argv[4]}

    options = getOptions(cellName, appInfo)
    print 'Completed the initialization successfully.'
    
    #uninstall
    if isAppExists(appInfo["appName"]):
        stopApp(appInfo["nodeName"], appInfo["serverName"], appInfo["appName"])
        removeApp(appInfo["appName"])
        save()
    
    #install
    installApp(appInfo["filePath"], options)
    save()
    #start application
    startApp(appInfo["nodeName"], appInfo["serverName"], appInfo["appName"])
