package main

import (
	"fmt"
	"plugin"
)

// LoadPlugin loads the specified shared library.
func LoadPlugin(path string) (*plugin.Plugin, error) {
	p, err := plugin.Open(path)
	if err != nil {
		return nil, err
	}
	return p, nil
}

// LookupSymbol looks up a symbol (function) in the loaded plugin.
func LookupSymbol(p *plugin.Plugin, symbolName string) (plugin.Symbol, error) {
	function, err := p.Lookup(symbolName)
	if err != nil {
		return nil, err
	}
	return function, nil
}
func main() {
	// Path to the plugin file
	pluginPath := "/code/src/webdemo/tmp/tmp.so"

	// Load the plugin
	importFile, err := LoadPlugin(pluginPath)
	if err != nil {
		fmt.Println("Error loading plugin:", err)
		return
	}

	// Lookup the function
	function, err := LookupSymbol(importFile, "Foo")
	if err != nil {
		fmt.Println("Error looking up symbol:", err)
		return
	}

	// Assert that the symbol is a function with the expected signature
	fooFunc, ok := function.(func(int, int) int)
	if !ok {
		fmt.Println("Symbol is not of type func(int, int) int")
		return
	}

	// Call the function with arguments
	result := fooFunc(1, 2)
	fmt.Println("Function returned:", result)
}
