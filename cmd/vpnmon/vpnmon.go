package main

import (
	log "github.com/sirupsen/logrus"
	"gopkg.in/alecthomas/kingpin.v2"
	"os"
	"path/filepath"
	"time"
	"vpnmon/internal/bandwidth"
	"vpnmon/internal/connectivity"
	"vpnmon/internal/metrics"
	"vpnmon/internal/version"
)

func main() {
	cfg := struct {
		port            int
		debug           bool
		interval        string
		openVPNProxy    string
		openVPNFilename string
		token           string
	}{}

	a := kingpin.New(filepath.Base(os.Args[0]), "media monitor")

	// TODO: parse url, interval up front and pass resulting data types to the probes
	a.Version(version.BuildVersion)
	a.HelpFlag.Short('h')
	a.VersionFlag.Short('v')
	a.Flag("debug", "Log debug messages").BoolVar(&cfg.debug)
	a.Flag("port", "API listener port").Default("8080").IntVar(&cfg.port)
	a.Flag("interval", "Time between measurements").Default("30s").StringVar(&cfg.interval)
	a.Flag("proxy", "OpenVPN proxy URL").Required().StringVar(&cfg.openVPNProxy)
	a.Flag("file", "OpenVPN status file").Required().StringVar(&cfg.openVPNFilename)
	a.Flag("token", "ipinfo.io authentication token").Required().StringVar(&cfg.token)

	_, err := a.Parse(os.Args[1:])
	if err != nil {
		a.Usage(os.Args[1:])
		os.Exit(2)
	}

	if cfg.debug {
		log.SetLevel(log.DebugLevel)
	}

	log.Info("openvpn monitor v" + version.BuildVersion)

	// Prometheus Metrics
	metrics.Init(cfg.port)

	// Connectivity probe
	log.Debugf("Starting connectivity probe")

	duration, err := time.ParseDuration(cfg.interval)
	if err != nil {
		log.Warningf("failed to parse duration '%s'. Defaulting to 5m", cfg.interval)
		duration = 5 * time.Minute
	}

	if probe, err := connectivity.NewProbe(cfg.openVPNProxy, cfg.token); err == nil {
		go func(probe *connectivity.Probe, duration time.Duration) {
			for {
				probe.Run()
				time.Sleep(duration)
			}
		}(probe, duration)
	} else {
		log.Warningf("could not start connectivity probe: %s", err.Error())
	}

	// Bandwidth probe
	log.Debug("Starting bandwidth probe")

	probe := bandwidth.NewProbe(cfg.openVPNFilename)

	go func(probe *bandwidth.Probe, duration time.Duration) {
		for {
			probe.Run()
			time.Sleep(duration)
		}
	}(probe, 5*time.Second)

	for {
		time.Sleep(30 * time.Second)
	}
}
