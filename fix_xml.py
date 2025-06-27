#!/usr/bin/env python3
import json
with open('app/services/kvm_service.py', 'r') as f:
    content = f.read()

# Исправляем XML тег
content = content.replace('  <n>{vm_name}</n>', '  <name>{vm_name}</name>')

with open('app/services/kvm_service.py', 'w') as f:
    f.write(content)

print("XML тег исправлен!")
