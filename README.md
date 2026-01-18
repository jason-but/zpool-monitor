# ZPool Monitor

This package provides a replacement for the standard `zpool status` command to monitor the status of ZPools on your system. Output is colour formatted for 
easier detection of errors and problems to address, progress of running tasks is displayed using a progress bar.

Future versions will support a full screen app with a regular refresh rate.

## Installation

Under development, not hosted on PiPi yet.

For now you are on your own

## Usage

```console
# zpool_mon -h
usage: zpool_mon [-h] [poolname ...]

🔍 ZPool Status Monitor

A 'pretty' replacement for the 'zpool status' command

positional arguments:
  poolname    ZPool name to monitor (default is all pools)

options:
  -h, --help  show this help message and exit

```

| Command-line Parameter | Description                                                                                                                                                                                                  |
|:-----------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `poolname`             | Same functionality as listing a pool when executing `zpool status [pool]`. If not specified, will default to scanning all pools on system. Can specify, 0(all pools), 1(single pool) or multiple pool names. |

## Execution

```console
# zpool_mon
────────────────────────────────────────────────────────────────────────────────────────────────────────── ZPool - jaybee_zfspool ──────────────────────────────────────────────────────────────────────────────────────────────────────────
                                  
  State:    ONLINE                
  Errors:   No known data errors  
                                  
 🔍 Details                                                                                                                                      
 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 
  Device Name      Size    State    Device                                              Read   Write   Checksum   Last Trim                      
 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 
  XXXXXX_zfspool   13.0T   ONLINE                                                       0      0       0                                         
    raidz1-0       13.0T   ONLINE                                                       0      0       0                                         
      bay_1_1      3.64T   ONLINE   ata-Samsung_SSD_870_EVO_4TB_XXXXXXXXXXXXXXX-part1   0      0       0          Sun 18 Jan 2026 12:01:33 AEDT  
      bay_1_2      3.64T   ONLINE   ata-CT4000MXXXXXXXX_XXXXXXXXXXXX-part1              0      0       0          Sun 18 Jan 2026 12:01:27 AEDT  
      bay_1_3      3.64T   ONLINE   ata-Samsung_SSD_870_EVO_4TB_XXXXXXXXXXXXXXX-part1   0      0       0          Sun 18 Jan 2026 12:01:34 AEDT  
      zfs_disk3    2.73T   ONLINE   ata-WDC_WD30EZRZ-00Z5HB0_WD-XXXXXXXXXXXX-part1      0      0       0                                         
      zfs_disk4    2.73T   ONLINE   ata-WDC_WD30EZRZ-00Z5HB0_WD-XXXXXXXXXXXX-part1      0      0       0                                         
      zfs_disk5    3.64T   ONLINE   ata-WDC_WD40EFRX-68N32N0_WD-XXXXXXXXXXXX-part1      0      0       0                                         
 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── 

 🧼 Scrub Status                                           
                                                           
  Last Scrub Finished:   🕓 Mon 12 Jan 2026 07:00:55 AEDT  
  Scanned:               🔍 6.88T                          
  Duration:              ⌛ 3:12:34                        
  Repaired:              🪛 0B with 0 errors               
 
```
