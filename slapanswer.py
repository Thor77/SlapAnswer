import random
import json
import znc


class slapanswer(znc.Module):
    description = 'Answer slaps'
    module_types = [znc.CModInfo.NetworkModule]

    def OnLoad(self, args, message):
        self.default_answers = [
            '"Be kind whenever possible. It is always possible." - Dalai Lama',
            '"Where ignorance is our master, there is no possibility of real'
            ' peace." - Dalai Lama',
            '"We can never obtain peace in the outer world until we make peace'
            ' with ourselves." - Dalai Lama',
            '"An eye for an eye will only make the whole world blind."'
            ' - Mahatma Gandhi',
            '"The best fighter is never angry" - Lao Tzu',
            '"Peace cannot be achieved through violence, it can only be'
            ' attained through understanding." - Ralph Waldo Emerson',
            '"Silence is sometimes the best answer" - Dalai Lama',
        ]
        if 'answers' in self.nv:
            self.ANSWERS = json.loads(self.nv['answers'])
        else:
            self.ANSWERS = self.default_answers
            self.save_answers()
        return True

    def OnModCommand(self, cmd):
        split = cmd.split()
        command = str(split[0]).lower()
        args = [a.lower() for a in split[1:]]
        if command == 'help':
            self.command_help()
        elif command == 'add':
            self.command_add(args)
        elif command == 'remove':
            self.command_remove(args)
        elif command == 'reset':
            self.command_reset()
        elif command == 'list':
            self.command_list()

    def save_answers(self):
        self.nv['answers'] = json.dumps(self.ANSWERS)

    def command_help(self):
        self.PutModule('\n'.join([
            'add <msg> | add a msg (replace nick with {nick})',
            'remove <id> | remove msg with id <id> (get id\'s with "list")',
            'reset | reset msgs to default',
            'list | get a list with msgs'
        ]))
        return True

    def command_add(self, args):
        msg = ' '.join(args)
        if '\n' in msg:
            self.PutModule('ERROR: Line-Breaks are not allowed in answers!')
            return True
        self.ANSWERS.append(msg)
        self.save_answers()
        self.PutModule('Successfully added answer!')
        return True

    def command_remove(self, args):
        try:
            answer_id = int(args[0])
        except ValueError:
            self.PutModule('ERROR: Invalid ID!')
        if answer_id < len(self.ANSWERS) and answer_id >= 0:
            del self.ANSWERS[answer_id]
            self.save_answers()
            self.PutModule('Successfully removed answer!')
        else:
            self.PutModule(
                'ERROR: Invalid ID! Try "list" for a list of id\'s!'
            )
        return True

    def command_reset(self):
        self.ANSWERS = self.default_answers
        self.save_answers()
        self.PutModule('Successfully reset answers!')
        return True

    def command_list(self):
        for index, value in enumerate(self.ANSWERS):
            self.PutModule('{} | {}'.format(index, value))
        return True

    def OnChanAction(self, invoker, channel, message):
        own_nick = self.GetNetwork().GetIRCNick().GetNick()
        own_host = self.GetNetwork().GetIRCNick().GetHostMask()
        nick = invoker.GetNick()
        channel = channel.GetName()
        msg = str(message)
        if 'slap' in msg and own_nick in msg:
            self.answer_slap(channel, nick, own_host)
        return znc.CONTINUE

    def answer_slap(self, channel, nick, own_host):
        msg = random.choice(self.ANSWERS)
        if '{nick}' in msg:
            msg = msg.format(nick=nick)
        msg = 'PRIVMSG {channel} :{msg}'.format(channel=channel, msg=msg)
        self.GetNetwork().PutIRC(msg)
        self.GetNetwork().PutUser(':{own_host} {msg}'.format(
            own_host=own_host, msg=msg))
