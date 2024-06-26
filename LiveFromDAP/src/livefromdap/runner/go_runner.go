package main

import (
	"fmt"
	"plugin"
)
var importFile *plugin.Plugin

// LoadPlugin loads the specified shared library and assigns it to importFile
func LoadPlugin(path string) error {
	var err error
	importFile, err = plugin.Open(path)
	if err != nil {
		return err
	}
	return nil
}

// LookupSymbol looks up a symbol (function) in the loaded plugin.
func LookupSymbol(symbolName string) (plugin.Symbol, error) {
	function, err := importFile.Lookup(symbolName)
	if err != nil {
		return nil, err
	}
	return function, nil
}
func main() {
	pluginPath := "/code/src/webdemo/tmp/tmp.so"

	err := LoadPlugin(pluginPath)
	if err != nil {
		fmt.Println("Error loading plugin:", err)
		return
	}

	function, err := LookupSymbol("Foo")
	if err != nil {
		fmt.Println("Error looking up symbol:", err)
		return
	}

	fooFunc, ok := function.(func(int, int) int)
	if !ok {
		fmt.Println("Symbol is not of type func(int, int) int")
		return
	}

	result := fooFunc(1, 2)
	fmt.Println("Function returned:", result)
}
