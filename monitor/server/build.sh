#!/bin/sh

export MONITOR_VERSION=rucio-con-mon:1.0.2
export HARBOR=registry.cern.ch/cmsrucio

podman build -t $HARBOR/$MONITOR_VERSION .
podman push $HARBOR/$MONITOR_VERSION


