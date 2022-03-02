list = []

with open('/var/log/ppp.log', 'r') as file:
  isStart = True
  for line in file.readlines():
    if isStart:
      d = dict()
      d['prevMess'] = ''
      isStart = False
    if len(line.split(' : ')) == 2:
        if 'L2TP disconnected' not in line:
            d['prevMess'] += line
        else:   
            d['Date'], d['Message'] = line.split(' : ', 1)
            list.append(d)
            isStart = True

print(list[-1])

