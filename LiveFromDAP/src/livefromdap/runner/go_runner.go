package main

import (
	"fmt"
	"plugin"
	"reflect"
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
func callPluginFunction(funcName string, args ...interface{}) ([]reflect.Value, error) {
	// Lookup the symbol
	symbol, err := importFile.Lookup(funcName)
	if err != nil {
		return nil, err
	}

	symbolValue := reflect.ValueOf(symbol)

	reflectArgs := make([]reflect.Value, len(args))
	for i, arg := range args {
		reflectArgs[i] = reflect.ValueOf(arg)
	}

	result := symbolValue.Call(reflectArgs)

	return result, nil
}
func main() {
	pluginPath := "/code/src/webdemo/tmp/tmp.so"

	err := LoadPlugin(pluginPath)
	if err != nil {
		fmt.Println("Error loading plugin:", err)
		return
	}

	fooResult, err := callPluginFunction("Foo", 3, 4)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Foo(3, 4) = %v\n", fooResult[0].Interface())
}
