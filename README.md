# mosaic-data

Public data for the [Mosaic](https://github.com/iammanpreetbhullar/Mosaic) Android TV launcher.

## `sgpc-calendar.json`: the Nanakshahi Jantri

The SGPC Nanakshahi calendar (Jantri): Gurpurabs, itihasik dihade, bhagat sahiban de dihade and
Sangrands, one entry per Nanakshahi year. Years read from a printed Jantri are `"confirmed"`; the next
few years are `"estimated"` from an astronomical model until their Jantri is published, and Mosaic marks
those dates with ≈.

It is a mirror of the data published by
[janpreet/nanakshahi-ical](https://github.com/janpreet/nanakshahi-ical) (engine:
[janpreet/nanakshahi-jantri](https://github.com/janpreet/nanakshahi-jantri)), © Janpreet Singh,
MIT licence (see [LICENSE-nanakshahi-ical](LICENSE-nanakshahi-ical)).

Mosaic TVs download this file about once a week, from:

```
https://raw.githubusercontent.com/iammanpreetbhullar/mosaic-data/main/sgpc-calendar.json
```

### Keeping it current

- **Automatically:** on the 2nd of every month the *Refresh Jantri data* workflow fetches the latest
  data, checks it, and opens a pull request if it changed. Review and merge it; TVs pick it up within
  a week. (Repository settings › Actions › General › allow GitHub Actions to create pull requests.)
- **By hand**, any time:

  ```bash
  python3 -I update.py update   # fetch, check, write sgpc-calendar.json
  python3 -I update.py check    # check only
  ```

Each March the new Jantri is added upstream; until then that year shows as estimated.
