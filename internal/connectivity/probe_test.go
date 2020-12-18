package connectivity_test

import (
	"bytes"
	"io/ioutil"
	"net/http"
	"testing"
	"vpnmon/internal/metrics"

	"github.com/clambin/httpstub"
	"github.com/stretchr/testify/assert"

	"vpnmon/internal/connectivity"
)

func TestNewProbe(t *testing.T) {
	for _, uri := range []string{"notaproxy", "not a proxy", ""} {
		probe, err := connectivity.NewProbe(uri, "")

		assert.Nil(t, probe, uri)
		assert.NotNil(t, err, uri)
	}
}

func TestProbe_Run(t *testing.T) {
	probe, err := connectivity.NewProbeWithHTTPClient(httpstub.NewTestClient(loopback), "")

	assert.Nil(t, err)

	probe.Run()

	value, ok := metrics.LoadValue("openvpn_client_status")
	assert.True(t, ok)
	assert.Equal(t, 1.0, value)
}

func TestProbe_Run_Fail(t *testing.T) {
	probe, err := connectivity.NewProbeWithHTTPClient(httpstub.NewTestClient(httpstub.Failing), "")

	assert.Nil(t, err)

	probe.Run()

	value, ok := metrics.LoadValue("openvpn_client_status")
	assert.True(t, ok)
	assert.Equal(t, 0.0, value)
}

// lookup function

func loopback(_ *http.Request) *http.Response {
	return &http.Response{
		StatusCode: 200,
		Body:       ioutil.NopCloser(bytes.NewBufferString(ipinfoResponse)),
	}
}

// Response

const ipinfoResponse = `{
  "ip": "1.2.3.4",
  "hostname": "example.com",
  "city": "City",
  "region": "Region",
  "country": "BE",
  "loc": "Loc",
  "org": "Org",
  "postal": "1234",
  "timezone": "Europe/Brussels"
}`
