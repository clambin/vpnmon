package metrics

import (
	"fmt"
	"net/http"
	"strings"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	log "github.com/sirupsen/logrus"
)

var (
	unlabeledGauges = map[string]prometheus.Gauge{
		"openvpn_client_status": promauto.NewGauge(prometheus.GaugeOpts{
			Name: "openvpn_client_status",
			Help: "OpenVPN Client Status",
		}),
		"openvpn_client_tcp_udp_read_bytes_total": promauto.NewGauge(prometheus.GaugeOpts{
			Name: "openvpn_client_tcp_udp_read_bytes_total",
			Help: "OpenVPN client bytes read",
		}),
		"openvpn_client_tcp_udp_write_bytes_total": promauto.NewGauge(prometheus.GaugeOpts{
			Name: "openvpn_client_tcp_udp_write_bytes_total",
			Help: "OpenVPN client bytes written",
		}),
	}

	cachedValues = map[string]map[string]float64{}
)

// Init initializes the prometheus metrics server
func Init(port int) {
	http.Handle("/metrics", promhttp.Handler())
	listenAddress := fmt.Sprintf(":%d", port)
	go func(listenAddr string) {
		err := http.ListenAndServe(listenAddress, nil)
		if err != nil {
			panic(err)
		}
	}(listenAddress)
}

// Publish pushes the specified metric to Prometheus
func Publish(metric string, value float64, labels ...string) bool {
	log.Debugf("%s(%s): %f", metric, labels, value)
	if gauge, ok := unlabeledGauges[metric]; ok {
		gauge.Set(value)
		SaveValue(metric, value, labels...)
		return true
	}

	log.Warningf("metric '%s' not found", metric)
	return false
}

// SaveValue stores the last value reported so unit tests can verify the correct value was reported
func SaveValue(metric string, value float64, labels ...string) {
	subMap, ok := cachedValues[metric]
	if ok == false {
		subMap = make(map[string]float64)
		cachedValues[metric] = subMap
	}
	key := strings.Join(labels, "|")
	subMap[key] = value
}

// LoadValue gets the last value reported so unit tests can verify the correct value was reported
func LoadValue(metric string, labels ...string) (float64, bool) {
	if value, ok := cachedValues[metric][strings.Join(labels, "|")]; ok {
		return value, true
	}
	return 0, false
}
