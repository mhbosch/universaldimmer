from core.actions import ScriptExecution
from core.log import logging, LOG_PREFIX, log_traceback
from core.rules import rule
from core.triggers import when
from core.actions import LogAction
from org.joda.time import DateTime



RULE_NAME="Universaldimmer JSR232"
log=logging.getLogger(LOG_PREFIX+"."+RULE_NAME)
iteration = 0


dimmertimers = {}


def DimNow(Item):
    try:
        global iteration
        interval = dimmertimers[Item]['FadeStepMS']

        if iteration >= (int(dimmertimers[Item]['loops'])):
            events.sendCommand(Item, int(str(dimmertimers[Item]['TargetValue'])))
            dimmertimers[Item]['timer'].cancel()
            iteration = 0
            dimmertimers[Item]['timer'] = None
            del dimmertimers[Item]
            return;
        else:
            NewPercent = round(float(str(items[Item])) - float(dimmertimers[Item]['PercentPerStep']),2)
            events.sendCommand(Item, str(NewPercent))
            dimmertimers[Item]['timer'].reschedule(DateTime.now().plusMillis(interval))
            iteration += 1

        dimmertimers[Item]['iteration'] = iteration 
    except:
        LogAction.logInfo("DimNow Routine", u"CleanUp" )
        dimmertimers[Item]['timer'].cancel()
        dimmertimers[Item]['timer'] = None
        del dimmertimers[Item]

@log_traceback
@rule(RULE_NAME, description="Universaldimmer fuer Openhab", tags=["sensor"])
@when("Item universaldimmer received command")
 
def dimmer(event):
    global iteration
    interval = 250
    Loops = 0
    Befehl = str(event.getItemCommand()).split(",")
    
    try:        #Fehlerbehebung bei fehlenden FadeStep
        FadeStepMS = int(Befehl[4])
    except (IndexError, ValueError):
        FadeStepMS = interval
 
    TargetValue = int(Befehl[1])
    FadePeriodMs = int(Befehl[2])
    Item = Befehl[3]

    try:
        StartValue =  items[Item]
    except(KeyError):       
        return;
    
    if items[Item] == NULL:
        LogAction.logInfo("Timer Test", u"Abbruch" )
        return;

    LogAction.logInfo("Timer Test", u"Item = " + Item)
    if Item in dimmertimers:
        LogAction.logInfo("Timer Test", u"Item existiert" )
        dimmertimers[Item]['timer'].cancel()
        dimmertimers[Item]['timer'] = None
        del dimmertimers[Item]

    PercentPerStep =  ((float(str(StartValue))) - float(str(TargetValue))) /(FadePeriodMs/FadeStepMS)
    if PercentPerStep == 0:
        LogAction.logInfo("Dimmer Routine", u"Nichts zu tun!")    
        return;

    Loops = FadePeriodMs/FadeStepMS
    
    dimmertimers[Item] = {  'item'              : Item,
                            'timer'             : ScriptExecution.createTimer(DateTime.now().plusMillis(interval), lambda: DimNow(Item)),
                            'loops'             : Loops,
                            'TargetValue'       : TargetValue,
                            'FadePeriod'        : FadePeriodMs,
                            'PercentPerStep'    : PercentPerStep,
                            'FadeStepMS'        : FadeStepMS
                                  }
   
    dimmertimers[Item]['timer'].reschedule(DateTime.now().plusMillis(interval))
    

@log_traceback
def scriptLoaded(*args):
    log.info(RULE_NAME+" loaded.")
    LogAction.logInfo("Timer Test", u" "+RULE_NAME+" geladen")
