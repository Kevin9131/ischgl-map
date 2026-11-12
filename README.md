# Ischgl · Silvretta Arena ski map

An interactive piste map of Ischgl (AT) and Samnaun (CH), built to use on your phone while skiing.

**Open it:** https://kevin9131.github.io/ischgl-map/

## Features

- **All pistes, lifts and mountain restaurants**, with arrows showing which way each lift and piste runs
- **Live lift and piste status**: shows what's open today, refreshed every 15 minutes during the season
- **Route planner**: get from A to B with only the lifts and pistes that are open, and pick the hardest colour you want to ski
- **Sun and shade**: real mountain shadows for any date and time, plus which restaurant terraces get sun
- **Weather at altitude** for the valley, the mid-stations and the peaks
- **Live GPS** showing where you are on the map
- **Meeting point**: long-press the map, set a time and share the link
- **My pistes**: import your Ski Tracks GPX/KML files to see which pistes you've boarded and which are still left
- **SOS**: ski patrol and emergency numbers, with your current position
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

A GitHub Action (`.github/workflows/lift-status.yml`) runs every 15 minutes from 07:00 to 17:45 Ischgl time, November to May. It runs `fetch_status.py`, which reads the resort's lift and piste status and writes `status.json`. The workflow only commits when something has changed. The app downloads `status.json` and only treats it as current if the resort has updated it today.

You can also start the workflow by hand: **Actions → Lift & piste status → Run workflow**.

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
- Map library: [Leaflet](https://leafletjs.com)

This is a personal project and not affiliated with the Silvretta Arena or the ski resort. Always check the official signs and the ski patrol on the mountain.
