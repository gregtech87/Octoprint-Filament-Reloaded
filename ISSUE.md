
Plugin stopped working, API is fine.

Created by: NeoCortex3

Hi @nickmitchko love your Plugin, been using it for years.

2 Weeks ago all of a sudden it stoped working for me. Since Octopi was nagging about my python beeing outdated soon, I thought it would be a good moment to update everything.

So I installed a new OctoPi image (clean install, not an update). I'm now on: OctoPrint 1.11.2 Python 3.11.2 OctoPi* 1.1.0 (build 2025.06.10.114348)

When I check the API via /plugin/filamentreload/status the sensor is read correctly. But OctoPi will just not see it. The circle in the navbar stays green, no matter if filament is present or not.

Any help would be appreciated, Julix.

Tasks
0

No tasks are currently assigned. Use tasks to break down this issue into smaller parts.
Linked items
0
Activity

    Nicholai Mitchko
    Nicholai Mitchko
    @nmitchko · 3 months ago
    Author Owner

    Created by: loroff

    @nickmitchko . bonjours idem pour moi l icone dans la barre de navigation reste verte en permanence je suis sous octoprint 1.11.3 python 3.11.2 octopi1.1.0cam . Je confirme egalement que sous la version suivante :octoprint1.11.3 python 3.9.2 octopi1.0.0c le plug in fonctionne parfaitement
    Nicholai Mitchko
    Nicholai Mitchko
    @nmitchko · 3 months ago
    Author Owner

    Created by: nickmitchko

    Hi @NeoCortex3 / @loroff. Thanks for letting me know. I will investigate.
    Nicholai Mitchko
    Nicholai Mitchko
    @nmitchko · 3 months ago
    Author Owner

    Created by: nickmitchko

    @NeoCortex3 What RPI version are you running? RPI4 or RPI5?
    Nicholai Mitchko
    Nicholai Mitchko
    @nmitchko · 3 months ago
    Author Owner

    Created by: loroff

    @nickmitchko bonjours j utilise le RPI4
    Nicholai Mitchko
    Nicholai Mitchko
    @nmitchko · 1 month ago
    Author Owner

    Created by: nickmitchko

    Thanks for your patience. The bug is related to the newer octoprint python + debian combination. Fix might be a little complicated. Will have to re-roll the plugin, might take a bit to get it working.