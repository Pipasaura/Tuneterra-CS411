def linkDresser(link):
    for i in range(len(link)):
        if link[i] == '?':
            link = link[:i + 1]
            break
    return link[:24] + '/embed' + link[24:] + 'utm_source=generator'

def playlistID(link):
    link = link[34:]
    for i in range(len(link)):
        if link[i] == '?':
            link = link[:i]
            break
    return link

def devicePicker(devices):
    for i in devices["devices"]:
        if i["is_active"] == True:
            device = i["id"]
        else:
            device = devices["devices"][0]["id"]
    return device
