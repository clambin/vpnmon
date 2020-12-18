package metrics_test

import (
	"github.com/stretchr/testify/assert"
	"testing"

	"vpnmon/internal/metrics"
)

func TestLoadValue(t *testing.T) {
	metrics.SaveValue("metric", 12, "label1", "label2")
	loaded, ok := metrics.LoadValue("metric", "label1", "label2")
	assert.True(t, ok)
	assert.Equal(t, float64(12), loaded)

	loaded, ok = metrics.LoadValue("metric", "label1", "label3")
	assert.False(t, ok)
}

func TestInit(t *testing.T) {
	assert.NotPanics(t, func() { metrics.Init(8080) })
	assert.Panics(t, func() { metrics.Init(8080) })
}

func TestPublish(t *testing.T) {
	// Invalid
	ok := metrics.Publish("not_a_metric", 1.0)
	assert.False(t, ok)

	// Valid
	var gauges = []string{
		"openvpn_client_status",
		"openvpn_client_tcp_udp_read_bytes_total",
		"openvpn_client_tcp_udp_write_bytes_total",
	}
	for _, gauge := range gauges {
		// Unlabeled Gauge
		ok := metrics.Publish(gauge, 50)
		assert.True(t, ok)

		value, ok := metrics.LoadValue(gauge)
		assert.True(t, ok)
		assert.Equal(t, 50.0, value)
	}
}
