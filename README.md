# eventdriventalk
Code samples from a talk on event-driven infrastructure, first presented at DevOpsDays Singapore in 2016

*DO NOT EVER USE THIS IN PRODUCTION. YOU HAVE BEEN WARNED.*

Slides from the talk itself are located in `/powerpoint`.

Overview and Warning
====================

This is a small example which illustrates the componenents most often found in event-driven automation.

This code is in no way intended to be run in production or anywhere at all, really. At any given point,
it might be completely broken or might set your hair on fire. ;]

It is, however, intended to be used as a springboard for understanding the concepts behind event-driven automation
and as a conceptual model from which you can build your own systems.

Event-Driven Concepts
=====================

Event-driven automation operates on the princple that events flow into a management nodes. These nodes
can be on dedicated management machines or as a component present on host machines.

The stream of events rides on some type of message-passing transport. The message transport chosen for
this example is the [excellent ZeroMQ project](http://zeromq.org). Events may contain any type of information,
be it monitoring information, information about containers which are being provisioned or torn down,
telemetry information, operating system data, information about the function of a hosted application
or events from a configuration management framework.

A key concept is that it must be very easy and very fast to enqueue a event on the bus and must provide
a minimal impact on the sender. It should be easy for developers to add event-sending hooks into their
software. Thus, ZeroMQ with its wide support is an excellent choice. Other message brokers, however,
would be nearly as easy to implement. Given the need, it would be trivial to support multiple messaging
systems.

As the events arrive at management nodes, they are routed through a decision engine. The decision engine
checks to see if the event is one which should be acted upon. If so, it proceeds to run the event through
a series of rules to determine if an action should be taken. If a rule matches, actions are taken
and the next rule is evaluated. More complex rules engines are obviously possible and desireable. One
good place to explore might be [Pyke](http://pyke.sourceforge.net/knowledge_bases/rule_bases.html).

As an event flows through the decision engine, various rules may check a series of registers. These
registers maintain an ongoing state by allowing events to modify a shared K/V store. These registers
can also be used to maintain and track state as an event flows through the decision engine on its
way to an eventual set of actions. As an event flows through the system, actions are appended.

As a rule exits the decision engine, if it contains actions to be performed they may either be performed
directly on the manager machine, such as calling a configuration management system to call out to
various componenets in an infrastructure to make change. Alternatively, the message can be published
to all connected hosts to be run. (Obviously, target some sort of target selection would be necessary
but the logic to manage all of that is outside the scope of what this code is intended to illustrate.)


Event-Driven Automation Daemons
===============================

In this example, an event-driven automation system is imagined which contains the following components:

## Actor

An `actor` is a daemon which listens on a host machine. It listens to requests for action from the Publisher
and performs them. In an event-driven automation system, the `actor` would sit directly on top of the
configuration-management system, or better yet, be a part of it.

## Manager

The `Manager` is a process which lives on one (or more) machines in a cluster of machines which is under
management. It is the job of the `Manager` to listen to events on an event bus and to route them through
a rules engine. If an event meets a given rule, it is routed to the Publisher to be broadcast and acted
upon by an Actor.

## Publisher

When the rules engine controlled by the `Manager` determines that an action should be undertaken, it
publishes the action to all listening actions.


Topology
========
                             +---------------+
                             | (Actor)       |
                             -----------------
                             | Manager       |<-------Events flow to Manager over event bus on demand (Push/pull)
                             |---------------|
                             | Publisher     |<-------Publisher listens to Manager over IPC (Push/pull)
                             +---------------+
                                    |
                                    |
                    ---------------------------------  <---Pub/sub 
                    |               |               |
                +--------+    +----------+   +-----------+
                | Actor  |    |   Actor  |   |   Actor   |
                +--------+    +----------+   +-----------+
 


The Publisher and Manager run in a single operating system, as separate processes.

The Manager may direct the Publisher to instruct Actors to Perform actions over the pub/sub interface.

If desired, the manager may also perform actions directly, such as calling out to an external service.


Loader System
=============

This system is built around the principles of pluggability. Each component subsystem can be loaded into
a Python dictionary and easily accessed. The logic to construct such a dictionary is in `core.loader`.

A dictionary returned by a loader consists of lookup keys in a dot-delimited fashion:

```
<role> . <module> . <function>
```

For example, the `register` directory contains modules which contain various functions. A module in the
`register` directory named `foo` which contained a function called `bar` would appear in the loaded
dictionary as `register.foo.bar`.


Telemetry
=========

The telemetry directory contains code samples that illustrate how to push a message on a logical message
bus to a manager.

## Load beacon
    The load beacon illustrates a very simple beacon that emits a system load average across an event bus
    to a manager node


Pluggable Subsystems
====================

Actions
-------

`Actions` happen as a result of events. For example, an event may get processed and an action may be taken
which declares that another event should be sent, or a message should be sent to a Slack channel, or a container
should be provisioned, or a route added to a load balancer.

When thinking about the concepts contained herein, it may be most useful to simply think of `Actions` as the
configuration management layer which is far better equipped to handle changes than some half-baked
Python scripts. ;]

Rules
-----

Rules are the heart of the event-driven infrastructure conceptional framework. So as to not over-complicate
this example, only trivial rules are provided. Each rule must return either `True` or `False`.

Rules are processed and if conditions are met, actions are performed either locally or remotely via
the Publisher.


Registers
---------

In the event that it is necessary to collect aggregate events, or to have a location for events to set a state
which other events can read from, a register is provided.



