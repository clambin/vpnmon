package bandwidth

import (
	"bufio"
	"os"
	"regexp"
	"strconv"
	"vpnmon/internal/metrics"

	log "github.com/sirupsen/logrus"
)

// Probe to measure Plex metrics
type Probe struct {
	filename string
}

// NewProbe creates a new Probe
func NewProbe(filename string) *Probe {
	return &Probe{filename: filename}
}

// Run the probe. Collect all requires metrics
func (probe *Probe) Run() {
	if stats, err := probe.getStats(); err == nil {
		log.Debugf("read: %d, write: %d", stats.clientTcpUdpRead, stats.clientTcpUdpWrite)
		metrics.Publish("openvpn_client_tcp_udp_read_bytes_total", float64(stats.clientTcpUdpRead))
		metrics.Publish("openvpn_client_tcp_udp_write_bytes_total", float64(stats.clientTcpUdpWrite))
	} else {
		metrics.Publish("openvpn_client_tcp_udp_read_bytes_total", 0.0)
		metrics.Publish("openvpn_client_tcp_udp_write_bytes_total", 0.0)
		log.Warningf("%s", err.Error())
	}
}

type openVPNStats struct {
	// clientAuthRead       int
	// clientPreCompress    int
	// clientPreDecompress  int
	// clientPostCompress   int
	// clientPostDecompress int
	clientTcpUdpRead  int
	clientTcpUdpWrite int
	// clientTunTapRead     int
	// clientTunTapWrite    int
}

func (probe *Probe) getStats() (openVPNStats, error) {
	var stats = openVPNStats{}

	r := regexp.MustCompile(`^(.+),(\d+)$`)

	file, err := os.Open(probe.filename)
	if err == nil {
		defer file.Close()

		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			log.Debug(scanner.Text())
			for _, match := range r.FindAllStringSubmatch(scanner.Text(), -1) {
				value, _ := strconv.Atoi(match[2])
				switch match[1] {
				case "TCP/UDP read bytes":
					stats.clientTcpUdpRead = value
				case "TCP/UDP write bytes":
					stats.clientTcpUdpWrite = value
				}
			}
		}
	}

	return stats, err
}
