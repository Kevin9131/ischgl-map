# Ischgl · Silvretta Arena ski map

An interactive piste map of Ischgl (AT) and Samnaun (CH), built to use on your phone while skiing.

**Open it:** https://kevin9131.github.io/ischgl-map/

## Features

- **All pistes, lifts and mountain restaurants**, with arrows showing which way each lift and piste runs
- **Live lift and piste status**: shows what's open right now, straight from the resort's own feed, refreshed every 3 minutes while the app is open
- **Route planner**: get from A to B with only the lifts and pistes that are open, and pick the hardest colour you want to ski
- **Sun and shade**: real mountain shadows for any date and time, plus which restaurant terraces get sun
- **Weather at altitude** for the valley, the mid-stations and the peaks
- **Live GPS** showing where you are on the map
- **Meeting point**: long-press the map, set a time and share the link
- **My pistes**: import your Ski Tracks GPX/KML files to see which pistes you've boarded and which are still left
- **Webcams**: the official Ischgl and Samnaun webcams, live streams and 360° panoramas on the map. Tap one to open it on ischgl.com
- **SOS**: ski patrol and emergency numbers, with your current position
- **Dark mode**: follows your phone's setting, or tap the 🌙 button to switch
- **Valley at the bottom**: switch between north-up and Ischgl at the bottom of the map
- **Works offline** once you've added it to your Home Screen

## Install on iPhone

1. Open https://kevin9131.github.io/ischgl-map/ in Safari.
2. Tap the menu icon ☰ next to the address → **Share** → **Add to Home Screen**.
3. From then on, open it from the icon on your Home Screen. It works full screen, uses GPS and keeps working without signal on the mountain.

On Android, open the link in Chrome and choose **Add to Home screen** from the ⋮ menu.

## My pistes (Ski Tracks import)

1. In Ski Tracks, export a day as **GPX** (or KML) and save it to Files.
2. In the map, tap **✓ Mine**, then **Import Ski Tracks files**, and pick one or more days.
3. Green shows where you've boarded. Grey is still to discover. A piste gets a ✓ once you've done at least half of it.

Your tracks stay on your own phone (in the browser's storage). Nothing is uploaded.

## How the live status works

The app reads the resort's live status feed (Intermaps, the same feed behind the official Ischgl piste map) directly from your phone, every 3 minutes while the app is open. It only treats the status as current if the resort has updated it today.

As a backup, a GitHub Action (`.github/workflows/lift-status.yml`) runs `fetch_status.py`, which writes the same status to `status.json`. The app uses that file only if the live feed can't be reached. GitHub runs scheduled jobs on a best-effort basis, so in practice this file is often a few hours old.

You can also start the workflow by hand: **Actions → Lift & piste status → Run workflow**.

### WhatsApp alerts (optional)

The status job can send you a WhatsApp message when a lift or piste opens that wasn't open the day before. It uses the free [CallMeBot](https://www.callmebot.com/blog/free-api-whatsapp-messages/) API for personal use.

1. Follow CallMeBot's WhatsApp setup to get your API key.
2. In the repo go to **Settings → Secrets and variables → Actions** and add two secrets: `CALLMEBOT_PHONE` (your number with country code, e.g. `+316…`) and `CALLMEBOT_APIKEY`.

The first run sends a confirmation message. Without the secrets, nothing is sent.


## Files

| File | What it is |
|---|---|
| `index.html` | The whole app in one file: map, data, terrain and code |
| `sw.js` | Service worker that makes the app work offline |
| `manifest.webmanifest`, `icon-*.png`, `apple-touch-icon.png` | Home Screen app settings and icons |
| `fetch_status.py` | Script that fetches the live lift and piste status |
| `status.json` | Latest lift and piste status, written by the Action |
| `.github/workflows/lift-status.yml` | Schedule for the status updates |

## Updating

Replace `index.html` and `sw.js` with the new versions. The service worker has a cache version number (`ischgl-map-vNN`). When it changes, phones pick up the new version the next time the app is opened with signal.

## Data and credits

- Piste and lift data © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors, via [OpenSkiMap](https://openskimap.org) / OpenSkiStats
- Terrain: Copernicus DEM GLO-30 © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018, provided under COPERNICUS by the European Union and ESA
- Weather: [Open-Meteo](https://open-meteo.com)
- Lift status: Silvretta Arena / Intermaps
- Webcams: © Ischgl / TVB Paznaun-Ischgl, opened on [ischgl.com](https://www.ischgl.com)
- Map library: [Leaflet](https://leafletjs.com)

This is a personal project and not affiliated with the Silvretta Arena or the ski resort. Always check the official signs and the ski patrol on the mountain.
