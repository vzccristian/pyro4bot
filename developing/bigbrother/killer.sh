#!/bin/bash
for KILLPID in `ps ax | grep 'pyro4bot_BB' | awk ' { print $1;}'`; do
  #echo $KILLPID;
  kill -9 $KILLPID 2>/dev/null;
done
