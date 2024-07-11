package main

import (
	"fmt"
	"plugin"
)
var importFile *plugin.Plugin

// LoadPlugin loads the specified shared library and assigns it to importFile
func loadPlugin(path string) error {
	var err error
	importFile, err = plugin.Open(path)
	if err != nil {
		return err
	}
	return nil
}

// LookupSymbol looks up a symbol (function) in the loaded plugin.
func callPluginFunction(funcName string, arg int) (int, error) {
	// Lookup the symbol
	symbol, err := importFile.Lookup(funcName)
	if err != nil {
		return 0, err
	}

	function, ok := symbol.(func(int) int)
	if !ok {
		return 0, fmt.Errorf("symbol is not of type func(int) int")
	}

	result := function(arg)
	return result, nil
}
func main() {
	for {
		pluginPath := "/code/src/webdemo/tmp/tmp.so"
		err := loadPlugin(pluginPath)
		if err != nil {
			fmt.Println("Error loading plugin:", err)
			return
		}
		fooResult, err := callPluginFunction("Foo", 1)
		if err != nil {
			panic(err)
		}
		fmt.Printf("Foo(arg) = %v\n", fooResult)
	}
}
