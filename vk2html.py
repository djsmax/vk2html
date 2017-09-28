import vk
import json
import time


class StoryWriter:
    """Implementing of VKOpt HTML messages saver"""

    ids = {}
    ## Here,ids is a simple dictionary with:
    ## { <user_id> : ( <user_name> , <user_photo_100> , <user_short_name> ) }
    ## In init you can specify ids manually,
    ## or set them None, and ids will'be
    ## automatically generated.
    _dates = (0,0)
    _msgcount = 0
    __aplayer = False
    __sticker_size = 'photo_256'
    __api = vk.API(v = 5.68)
    ## Default API class,used for generating "ids" value.
    _failed = []

    def __init__(self,dialog,ids = None,audio_player = False,sticker_size = 'photo_256'):
        if not len(dialog):
            raise RuntimeError("No messages to render!")
        if ids:
            self.ids = ids
        if not sticker_size in ['photo_64','photo_128','photo_256','photo_352','photo_512']:
            raise ValueError("sticker_size must be in ['photo_64','photo_128','photo_256','photo_352','photo_512']")
        self.__aplayer = audio_player
        self._dates = (dialog[0]['date'],dialog[-1]['date'])
        self._msgcount = len(dialog)

    def _hrtime(self,secs):
        return time.strftime("%d.%m.%Y %H:%M:%S",time.gmtime(secs))


    def _userinfo(self,userid):
        i = self.__api.users.get(user_ids = userid,fields = 'photo_100,short_name')
        if 'short_name' in i:
            return ("%s %s" % (i['first_name'],i['last_name']),i['photo_100'],i['id'],i['short_name'])
        else:
            return ("%s %s" % (i['first_name'],i['last_name']),i['photo_100'],i['id'],'')


    def _vksget(self,a):
        "This method loks for best image resolution,returns most high one"
        if 'photo_2560' in a:
            return a['photo_2560']
        elif 'photo_1280' in a:
            return a['photo_1280']
        elif 'photo_807' in a:
            return a['photo_807']
        elif 'photo_604' in a:
            return a['photo_604']
        elif 'photo_130' in a:
            return a['photo_130']
        elif 'photo_75' in a:
            return a['photo_75']
        else:
            print("Unkown image size: \n%s" % a)
            return ''

    def _head(self):
        if self.__aplayer:
            addify = '<script>\nfunction audio_play() {\n  var vk_audio = document.getElementById("vk_audio");\n  if (vk_audio.paused) {\n    vk_audio.play();\n  } else {\n    vk_audio.pause();\n  }\n}\n</script>'
        else:
            addify = ''
        return '<!DOCTYPE html>\n         <html>\n            <!-- Created by https://github.com/djsmax/ --><head>\n               <meta charset="utf-8"/>\n               <link rel="shortcut icon" href="http://vk.com/images/icons/favicons/fav_logo.ico"/>\n               <title>VK Messages: %s </title>\n               <style>\n                  h4{font-family: inherit;font-weight: 500;line-height: 1.1;color: inherit;margin-top: 10px;margin-bottom: 10px;font-size: 18px;}\n                  body{font-family: "Helvetica Neue",Helvetica,Arial,sans-serif;font-size: 14px;line-height: 1.42857143;color: #333;background-color: #fff;margin:0;}\n                  hr{height: 0;margin-top: 20px;margin-bottom: 20px;border: 0;border-top: 1px solid #eee;}\n                  .messages{width:1170px;margin:0 auto;text-align:left;}\n                  .msg_item {overflow:hidden}\n                  .from,.msg_body,.att_head,.attacments,.attacment,.fwd{margin-left:60px;min-height: 1px;padding-right: 15px;padding-left: 15px;}\n                  .msg_item{margin-top:5px;}\n                  .upic{float:left}\n                  .upic img{vertical-align:top;padding:5px;width: 50px;height: 50px;}\n                  .round_upic .upic img{border-radius: 50%%;}\n                  a {color: #337ab7;text-decoration: none;}\n                  a:active, a:hover {outline: 0;}\n                  a:focus, a:hover {color: #23527c;text-decoration: underline;}\n                  .att_head{color:#777;}\n                  .att_ico{float:left;width:11px;height:11px;margin: 3px 3px 2px; background-image:url(\'http://vk.com/images/icons/mono_iconset.gif\');}\n                  .att_photo{background-position: 0 -30px;}\n                  .att_audio{background-position: 0 -222px;}\n                  .att_video{background-position: 0 -75px;}\n                  .att_doc{background-position: 0 -280px;}\n                  .att_wall,.att_fwd{background-position: 0 -194px;}\n                  .att_gift{background-position: 0 -105px;}\n                  .att_sticker{background-position: 0 -362px; width: 12px; height: 12px;}\n                  .att_link{background-position: 0 -237px;}\n                  .attb_link a span{color:#777777 !important;}\n                  .att_geo{background-position: 0 -165px;}\n                  .fwd{border:2px solid #C3D1E0;border-width: 0 0 0 2px;margin-left:85px;}\n               </style>\n%s\n            </head>\n' % \
               (self._getmembers(self.ids),addify)

    def _body(self):
        return '<body><div class="messages round_upic"><h4> Даты сообщений: с %s по %s </h4><h4> Всего сообщений: %i </h4><hr>\n\n' % \
               (self._hrtime(self._dates[0]),self._hrtime(self._dates[1]),self._msgcount)

    def _msg(self,msg):
        ##FIXME: Messages in peers
        hrdate = self._hrtime(msg['date'])
        id = msg['from_id']
        if id in self.ids:
            user = self.ids[id][0]
            user_img = self.ids[id][1]
            user_link = 'http://vk.com/id%s' % id
            user_short = self.ids[id][3]
        else:
            print("Getting info: id%i" % id)
            self.ids[id] = self._userinfo(id)
            user = self.ids[id][0]
            user_img = self.ids[id][1]
            user_link = 'http://vk.com/id%s' % id
            user_short = self.ids[id][3]
        if not msg['body'] == '':
            msgbody = '\n\t\t<div class="msg_body">%s</div>' % msg['body']
        else:
            msgbody = ''
        if 'attachments' in msg:
            att = '\n\t' + self._getatt(msg['attachments'])
        else:
            att = ''
        return '<div id="msg{id}" class="msg_item"><a name="msg{id}"></a>\n\t<div class="upic"><img src="{user_img}" alt="[photo_100]"></div>\n\t<div class="from"> <b>{user}</b> <a href="{user_link}" target="_blank">@{user_short}</a> \n\t<a href="#msg{id}">{hrdate}</a></div>{msgbody}{att}\n</div>\n\n'.format( \
                id = msg['id'],user_img = user_img,user = user,user_link = user_link,user_short = user_short,hrdate = hrdate,msgbody = msgbody,att = att)

    def _end(self):
        "Returns end of HTML document"
        return "<hr></div></body></html>"

    def _getmembers(self,ids):
        "Returns stirng 'Name Surname (id)' for each id"
        s = ""
        if not len(ids):
            return ""
        for id in ids:
            s += "%s (%i), " % (self.ids[id][0],id)
        return s[-1]

    def _getatt(self,attach):
        "Converts JSON attachments array to HTML tags"
        if attach:
            att = ''
            att_req = True
            #att = '<div class="attacments"><b>Материалы:</b></div>\n\t'
            for a in attach:
                try:
                    att += '<div class="attacment">'
                    ## TODO: All media types
                    ## currently:
                    ## photo,video,audio,doc,wall
                    ## sticker,audiomessage
                    ## in progress:
                    ## forward,geo
                    if a['type'] == 'photo':
                        aa = a['photo']
                        att += '<div class="att_ico att_photo"></div>\n\t\t'
                        att += '<a target="_blank" href="%s">%s [photo%s_%s] (%sx%s)</a>' % (self._vksget(aa),aa['text'],aa['owner_id'],aa['id'],aa['width'],aa['height'])
                    elif a['type'] == 'video':
                        aa = a['video']
                        att += '<div class="att_ico att_video"></div>\n\t\t'
                        att += '<a href="http://vk.com/video-%i_%i" target="_blank">[video-%i_%i] %s (%s)</a>' % (abs(aa['owner_id']),aa['id'],abs(aa['owner_id']),aa['id'],aa['title'],time.strftime('%M:%S',time.gmtime(aa['duration'])))
                    elif a['type'] == 'audio':
                        aa = a['audio']
                        att += '<div class="att_ico att_audio"></div\n\t\t'
                        if self.__aplayer:
                            addify = '<audio id="vk_audio" \n\t<source src="%s" type="audio/mp3" />\n</audio>\n<button type="button" onclick="audio_play()">&#9658;</button>' % (aa['url'])
                            # Implementing simple HTML5 audio
                            ## FIXME: audio type support,current mp3 only
                        else:
                            addify = ''
                        att += '%s  <a target="_blank" href="%s">[audio%i_%i] %s - %s (%s)</a>' % (addify,aa['url'],aa['owner_id'],aa['id'],aa['artist'],aa['title'],time.strftime("%M:%S",time.gmtime(aa['duration'])))
                    elif a['type'] == 'doc':
                        aa = a['doc']
                        if 'preview' in aa:
                            if 'audio_msg' in aa['preview']:
                                if self.__aplayer:
                                    att += '<audio id="vk_audio" \n\t<source src="%s" type="audio/mp3" />\n\t<button type="button" onclick="audio_play()">&#9658;</button>\n\t' % (aa['preview']['audio_msg']['link_mp3'])
                                    att += '<a target="_blank" href="%s">Голосовое сообщение (%i с.)</a>' % (aa['preview']['audio_msg']['link_mp3'],aa['preview']['audio_msg']['duration'])
                                else:
                                    att += '<div class="att_ico att_audio"></div>\n\t\t'
                                    att += '<a target="_blank" href="%s">Голосовое сообщение (%i с.)</a>' % (aa['preview']['audio_msg']['link_mp3'],aa['preview']['audio_msg']['duration'])
                        else:
                            att += '<div class="att_ico att_doc"></div>\n\t\t'
                            att += '<a target="_blank" href="%s">%s</a>' % (aa['url'],aa['title'])
                    elif a['type'] == 'wall':
                        aa = a['wall']
                        att += '<div class="att_ico att_wall"></div>\n\t\t'
                        att += '<a target="_blank" href="http://vk.com/wall-%i_%i">[wall-%i_%i]</a>' % (abs(aa['from_id']),aa['id'],abs(aa['from_id']),aa['id'])
                    elif a['type'] == 'sticker':
                        aa = a['sticker']
                        att_req = False
                        ## TODO/FIXME: Check for stciker rendering
                        att += '<img src="%s" alt="[sticker%i:%i]">' % (aa[self.__sticker_size],aa['product_id'],aa['id'])
                    else:
                        print("Unknown type: %s" % a['type'])
                    att += '</div>'
                except:
                    self._failed.append(a)
                    att += '</div>'
            if att_req:
                return '<div class="attacments"><b>Материалы:</b></div>\n\t' + att ##+ '\n\t</div>'
        else:
            att = ''
        return att

    def write_dialog(self,dialog):
        """Writes a dialog to HTML.
        Dialog form is a list with VK Message objects."""
        html = ""
        thto = ""
        for message in dialog:
            if dialog.index(message) % 1000 == 0:
                print("Message %i of %i" % (dialog.index(message),len(dialog)))
            thto += self._msg(message)
        html += self._head()
        html += self._body()
        html += thto
        html += self._end()
        return html


history = json.load(open('NK_KU.json','rb'))[:1000]
w = {}
w[253860421] = ("Кристина Усенкова","",253860421,'')
w[161550781] = ("Настя Казакова","",161550781,'')
rnd = StoryWriter(history,audio_player = False,ids = w)
a = rnd.write_dialog(history)
print(open('NK_KU.html','w',encoding = 'utf-8').write(a))
