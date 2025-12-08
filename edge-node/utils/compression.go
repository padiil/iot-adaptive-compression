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
	var b bytes.Buffer
	w := lz4.NewWriter(&b)
	w.Write(input)
	w.Close()
	return b.Bytes()
}
