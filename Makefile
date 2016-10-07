#!/usr/bin/make -f
# -*- mode:makefile -*-

icegridadmin=icegridadmin --Ice.Config=locator.config -uuser -ppass -e

DIREC_N1=user@vgcnode1.local

DIREC_N2=user@vgcnode2.local

DIREC_N3=user@vgcnode3.local

DIREC_N4=user@jmfgm-node1.local
DIREC_N5=user@jmfgm-node2.local
DIREC_N6=user@jmfgm-node3.local

all: nodoVirtual run icegrid

run-server: nodoVirtual run icegrid

z:
	$(icegridadmin) "node list" | tee nodelist.out
	for number in $(shell cat nodelist.out); do \
		echo $$number; \
	done

dir: /tmp/db/registry /tmp/db/node1 /tmp/db/node2 /tmp/db/node3 /tmp/cannon/

run: 
	ssh $(DIREC_N1) icegridnode --Ice.Config=node1.config &
	while ! ssh $(DIREC_N1) netstat -lptn 2> /dev/null | grep ":4061"; do sleep 1; done
	ssh $(DIREC_N2) icegridnode --Ice.Config=node2.config &
	ssh $(DIREC_N3) icegridnode --Ice.Config=node3.config &
	ssh $(DIREC_N4) icegridnode --Ice.Config=node4.config &
	ssh $(DIREC_N5) icegridnode --Ice.Config=node5.config &
	ssh $(DIREC_N6) icegridnode --Ice.Config=node6.config &
	ssh $(DIREC_N1) icepatch2calc /tmp/cannon/

	$(icegridadmin) "node list" | tee nodelist.out


icegrid: 

	$(icegridadmin) "application add cannon.xml"

#for node in $(shell cat nodelist.out); do \
#$(icegridadmin) "server template instantiate cannonApplication $$node ProcessorFactoryTemplate  $(shell cat index)"; \
#echo "$(shell cat index) +1" >> index; \
#done
	$(icegridadmin) "server template instantiate cannonApplication vgcnode1 ProcessorFactoryTemplate index=1"
	$(icegridadmin) "server template instantiate cannonApplication vgcnode2 ProcessorFactoryTemplate index=2"
	$(icegridadmin) "server template instantiate cannonApplication vgcnode3 ProcessorFactoryTemplate index=3"
	$(icegridadmin) "server template instantiate cannonApplication jmfgm-node1 ProcessorFactoryTemplate index=4"
	$(icegridadmin) "server template instantiate cannonApplication jmfgm-node2 ProcessorFactoryTemplate index=5"
	$(icegridadmin) "server template instantiate cannonApplication jmfgm-node3 ProcessorFactoryTemplate index=6"
	$(icegridadmin) "server start ProcessorFactoryServer1"
	$(icegridadmin) "server start ProcessorFactoryServer2"
	$(icegridadmin) "server start ProcessorFactoryServer3"
	$(icegridadmin) "server start ProcessorFactoryServer4"
	$(icegridadmin) "server start ProcessorFactoryServer5"
	$(icegridadmin) "server start ProcessorFactoryServer6"
	$(icegridadmin) "server start FrontendServer"



clean:  stopNode  removeDir

stopNode: removeApp

	for node in $(shell cat nodelist.out); do \
	    icegridadmin --Ice.Config=locator.config -u user -p pass -e "node shutdown $$node"; \
	done
	icegridadmin --Ice.Config=locator.config -u user -p pass -e "registry shutdown"



removeDir:
	-$(RM) nodelist.out
	ssh $(DIREC_N1) rm -r /tmp/db
	ssh $(DIREC_N1) rm -r /tmp/cannon
	ssh $(DIREC_N2) rm -r /home/user/*
	ssh $(DIREC_N3) rm -r /home/user/*


removeApp:
	icegridadmin --Ice.Config=locator.config -uuser -ppass -e "application remove cannonApplication"

run-client:
	python client.py --Ice.Config=locator.config --Ice.MessageSizeMax=2570000

/tmp/%:
	mkdir -p $@

nodeList:
	$(icegridadmin) "node list" | tee nodelist.out



nodoVirtual:

	ssh $(DIREC_N1) mkdir -p /tmp/db/node1 /tmp/db/registry /tmp/cannon/
	scp *.ice processor.py node1.config locator.config matrix_utils.py container.py $(DIREC_N1):/home/user/
	scp -r /home/gualdras/cannon/*.ice /home/gualdras/cannon/*.py /home/gualdras/cannon/*.config $(DIREC_N1):/tmp/cannon/

	ssh $(DIREC_N2) mkdir -p /tmp/db/node2
	scp *.ice processor.py node2.config locator.config matrix_utils.py container.py $(DIREC_N2):/home/user/

	ssh $(DIREC_N3) mkdir -p /tmp/db/node3
	scp *.ice processor.py node3.config locator.config matrix_utils.py container.py $(DIREC_N3):/home/user/


	ssh $(DIREC_N4) mkdir -p /tmp/db/node2
	scp *.ice processor.py node4.config locator.config matrix_utils.py container.py $(DIREC_N4):/home/user/

	ssh $(DIREC_N5) mkdir -p /tmp/db/node2
	scp *.ice processor.py node5.config locator.config matrix_utils.py container.py $(DIREC_N5):/home/user/

	ssh $(DIREC_N6) mkdir -p /tmp/db/node2
	scp *.ice processor.py node6.config locator.config matrix_utils.py container.py $(DIREC_N6):/home/user/
