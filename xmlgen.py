import datetime

def genxml(uris, display_duration, transition_duration):

	xml = ''
	now = datetime.datetime.now() - datetime.timedelta(weeks=2)

	starttime = '''
	<starttime>
		<year>%s</year>
		<month>01</month>
		<day>01</day>
		<hour>00</hour>
		<minute>00</minute>
		<second>00</second>
	</starttime>
''' % (now.year)

	transitions = ''

	for index in range(len(uris)):
		transitions += '''
	<static>
		<duration>%s</duration>
		<file>%s</file>
	</static>
	<transition>
		<duration>%s</duration>
		<from>%s</from>
		<to>%s</to>
	</transition>
''' % (display_duration, uris[index], transition_duration, uris[index], uris[(index+1)%len(uris)])

	return '''
<backgrounds>
%s
%s
</backgrounds>
''' % (starttime, transitions)

foo = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
print genxml(foo, 15, 1)	