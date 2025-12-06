package utils

import (
	"bytes"
	"compress/zlib"

	"github.com/pierrec/lz4/v4"
)

func CompressGzip(input []byte) []byte {
	var b bytes.Buffer
	w := zlib.NewWriter(&b)
	w.Write(input)
	w.Close()
	return b.Bytes()
}

func CompressLz4(input []byte) []byte {
	buf := make([]byte, lz4.CompressBlockBound(len(input)))
	n, err := lz4.CompressBlock(input, buf, nil)
	if err != nil {
		return input
	}
	return buf[:n]
}
