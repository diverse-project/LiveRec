package main

import (
	"fmt"
	"plugin"
)
var importFile *plugin.Plugin
var funcName string
var arg int

// LoadPlugin loads the specified shared library and assigns it to importFile
func loadPlugin(path string) error {
	var err error
	importFile, err = plugin.Open(path)
	if err != nil {
		return err
	}
	return nil
}
func setParam(name string, argument int){
	funcName = name
	arg = argument
}

// LookupSymbol looks up a symbol (function) in the loaded plugin.
func callPluginFunction() (int, error) {
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
	setParam("Foo",1)
	for {
		pluginPath := "/code/src/webdemo/tmp/tmp.so"
		err := loadPlugin(pluginPath)
		if err != nil {
			fmt.Println("Error loading plugin:", err)
			return
		}
		fooResult, err := callPluginFunction()
		if err != nil {
			panic(err)
		}
		fmt.Printf("Foo(arg) = %v\n", fooResult)
	}
}
