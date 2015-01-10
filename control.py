#!/usr/bin/env python
#
# Send LIRC commands to control Lego power functions from the Scratch
# programming environment.
#
# A single optional argument can specify the host where Scratch is
# running. If the argument is not provided the program connects to
# the local host.
#
#  Copyright 2015 Diomidis Spinellis
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#


import scratch
from subprocess import call
import sys

# Connect to Scratch host; by default on local host
hostname = 'localhost'
if len(sys.argv) == 2:
    hostname = sys.argv[1]
s = scratch.Scratch(host=hostname)


# Receive and queue Scratch messages
def listen():
    while True:
        try:
            yield s.receive()
        except scratch.ScratchError:
            raise StopIteration

# Now you can iterate over all the messages from Scratch
for msg in listen():
    # Can be sensor-update or broadcast
    if msg[0] != 'broadcast':
        continue
    # Scratch message is e.g. "Lego 2 blue -4" or "Lego 4 r brake"
    # to move backward channel 2 blue at power level 4 or brake 4 red
    data = msg[1].split()

    # Verify and assemble the command
    if data[0].upper() != 'LEGO' or len(data) != 4:
        continue

    # Channel #
    if data[1] not in [str(c) for c in range(1, 5)]:
        print "Channel not 1-4: " + data[1]
        continue
    cmd = data[1]

    # Red or blue side
    if data[2][0].upper() not in ('R', 'B'):
        print "Side not red or blue: " + data[2]
        continue
    cmd += data[2][0].upper()

    # PWM power or brake
    if data[3].upper() == 'BRAKE':
        cmd += '_BRAKE'
    elif data[3] in [str(p) for p in range(-7, 0)]:
        cmd += "_M" + data[3][1]
    elif data[3] in [str(p) for p in range(0, 8)]:
        cmd += "_" + data[3]
    else:
        print "Power not -7 to 7 or brake: " + data[3]
        continue

    print "Sending " + cmd
    call(['irsend', 'SEND_ONCE', 'LEGO_Single_Output', cmd])
