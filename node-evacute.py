#!/usr/bin/python
# -*- coding: UTF-8 -*-

import httplib, urllib, ssl,socket
import json,base64
import commands
import os
import re

if __name__ == '__main__':
    (status, output) = commands.getstatusoutput('oc get node -o json')
    if(status == 0):
        node_list = [{'name': x['metadata']['name'], 'type':x['status']['conditions'][1]['type']} for x in json.loads(output)['items'] ] 
        
        for node_item in  node_list:
            oadm_sche_node='oadm manage-node {0} --schedulable {1}'
            print(oadm_sche_node.format(node_item['name'],'false'))
            #(status, output) = commands.getstatusoutput(oadm_manage_node.format(node_item['name'],'false') )
            (status, output) = commands.getstatusoutput('oc get pods --all-namespaces -o json') 
            pod_list = [{'name': x['metadata']['name'], 
                        'namespace':x['metadata']['namespace'],
                        'nodename':x['spec']['nodeName'],
                        'phase': x['status']['phase'],
                        'generateName':x['metadata']['generateName'][:-1]}
                        for x in json.loads(output)['items'] 
                        if ( x['status']['phase']=='Running' and x['spec']['nodeName']==node_item['name'] ) ]
            print pod_list
            get_rc_template='oc get rc {0} -n {1} | sed 1d | awk \'{{print "{{\\\"DESIRED\\\":"$2", \\\"CURRENT\\\":"$3"}}"}}\''
            rc_scale='oc scale rc {0} --replicas={1} -n {2}'
            print get_rc_template
            
            for pod_item in pod_list:
                print(get_rc_template.format(pod_item['generateName'], pod_item['namespace']))
                (status, rc_status)=commands.getstatusoutput(get_rc_template.format(pod_item['generateName'], pod_item['namespace']))
                rc_status=json.loads(rc_status)
                print( rc_scale.format(pod_item['generateName'], rc_status['DESIRED']+1, pod_item['namespace'] ))
            
            oadm_evac_node='oadm manage-node {0} --evacuate'
            print(oadm_evac_node.format(node_item['name']))
            
            for pod_item in pod_list:
                print(get_rc_template.format(pod_item['generateName'], pod_item['namespace']))
                (status, rc_status)=commands.getstatusoutput(get_rc_template.format(pod_item['generateName'], pod_item['namespace']))
                rc_status=json.loads(rc_status)
                print( rc_scale.format(pod_item['generateName'], rc_status['DESIRED']-1, pod_item['namespace'] ))

            print(oadm_sche_node.format(node_item['name'],'true'))
    else:
        print output
