"""Authored, parameterized explainers. Each beat pairs a caption with a diagram label."""
import math
TOPICS=('echo','pendulum','wave','fall','orbit','shadow','circle')
def story(topic, variant):
    v=variant
    if topic=='echo':
        d=170+5*v; t=2*d/340
        return 'Can you measure a cliff with a clap?',[(f'Imagine a cliff {d} metres away. You clap once. What does the echo tell you?',f'{d} m to cliff'),('The sound travels to the rock and back. Your stopwatch measures both legs, not just one.','outward + return'),(f'At about 340 metres per second, the round trip takes {t:.2f} seconds.',f'{2*d} m round trip'),('Multiply the time by the speed of sound, then halve the result. That last step gives you the distance to the cliff.','distance = speed × time / 2')]
    if topic=='pendulum':
        k=2+v%6; L=1+v//6; t=2*math.pi*math.sqrt(k*k*L/9.81)
        return 'What if a swing had a longer rope?',[(f'Two swings start at the same small angle. One rope is {k*k} times as long. Which swing comes back first?',f'length ratio   1 : {k*k}'),('Watch the short swing. Its bob travels a shorter arc, and its direction changes more quickly.','short rope / long rope'),(f'For small swings, period scales with the square root of length. The longer swing takes {k} times as long per cycle.',f'period ratio   1 : {k}'),(f'On Earth, with the longer rope measuring {k*k*L} metres, one complete cycle takes about {t:.1f} seconds.',f'long swing   {t:.1f} s / cycle')]
    if topic=='wave':
        f=2+v; speed=12
        return 'What changes when a wave speeds up its beat?',[(f'Imagine a ripple train moving at twelve metres per second. The source makes {f} crests each second.','wave speed   12 m/s'),('The glowing dot marks one spot. Count how often a crest passes it. That rate is the frequency.','frequency = crests per second'),(f'Divide the speed by the frequency. Adjacent crests are about {speed/f:.2f} metres apart.',f'wavelength   {speed/f:.2f} m'),('Now double the beat without changing wave speed. Twice as many crests must fit in the same stretch. Their spacing halves.','double frequency / half spacing')]
    if topic=='fall':
        t=2+v; d=.5*9.81*t*t
        return 'Why do falling objects leave widening gaps?',[(f'Drop a ball from rest. Imagine taking one photo each second for {t} seconds. Ignore air resistance.',f'elapsed time   {t} s'),('The early dots bunch together. Gravity keeps adding speed, so the ball covers more ground in every new second.','dots mark equal times'),(f'With constant Earth gravity, distance is half the acceleration times time squared. Our ball falls about {d:.1f} metres.',f'distance   {d:.1f} m'),('Look halfway down the clock, not halfway down the track. Half the time means only a quarter of the distance.','half the time / quarter the drop')]
    if topic=='orbit':
        r=2+v; k=r**1.5
        return 'What if a planet orbited farther out?',[(f'Imagine two planets in circular orbits around one star. The outer orbit has {r} times the radius.',f'radius ratio   1 : {r}'),('The outer planet has a longer path. But that is only half the story. It also travels more slowly.','longer path / lower speed'),('Farther from the star, gravity is weaker. A slower speed is enough to keep the planet on a circular path.','same star / circular orbits'),(f'Kepler’s law combines both effects. Raise the radius ratio to the power of one and a half. The outer year is about {k:.2f} inner years.',f'year ratio   1 : {k:.2f}')]
    if topic=='shadow':
        h=3+v; a=[30,45,60][v%3]; s=h/math.tan(math.radians(a))
        return 'Can a shadow tell you the height of a pole?',[(f'Picture a vertical pole on level ground. The Sun sits {a} degrees above the horizon.',f'Sun elevation   {a}°'),('Trace a ray from the top of the pole to the tip of its shadow. The ray closes a right triangle.','pole + shadow + ray'),(f'The shadow is about {s:.2f} metres long. Multiply by the tangent of the Sun angle to find the height.',f'shadow   {s:.2f} m'),(f'The pole is about {h} metres tall. A lower Sun would stretch the shadow, even though the pole has not changed.',f'pole height   {h} m')]
    if topic=='circle':
        r=2+v; k=2+v%4
        return 'What if a circular garden grew wider?',[(f'A round garden has a radius of {r} metres. Imagine stretching that radius by a factor of {k}.',f'radius   {r} → {r*k} m'),('The outline grows in just one dimension. Its length scales by the same factor as the radius.',f'edge length   × {k}'),('But the ground inside expands in two directions. Every little patch grows wider and taller.',f'width × {k} / height × {k}'),(f'The new garden needs {k*k} times the turf, but only {k} times the fence. Area and perimeter answer different shopping questions.',f'turf   × {k*k}     fence   × {k}')]
    raise ValueError(topic)
