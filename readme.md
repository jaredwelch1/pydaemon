# PyDaemon

PyDaemon is a base class for implementing daemon processes using python. 

Proper usage is to create a subclass implementing the run() method for your desired functionality. Normally
the run method will poll for work to do in the background, possibly with callbacks for specific actions
