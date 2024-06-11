package main

import (
	"fmt"
	_ "os"
	"reflect"
	_ "runtime"
	"syscall"
	"time"
)

var targetFunction reflect.Value
var targetArgs []reflect.Value
var lastPath string

func loadFile(filename string) {
	if lastPath != "" {
		if err := syscall.Unlink(lastPath); err != nil {
			fmt.Println("Error removing last file:", err)
		}
	}
	lastPath = filename

	// Your file loading logic here
	fmt.Println("Loading file:", filename)

	// For demonstration, I'll just print the content
	content := fmt.Sprintf("Content of %s", filename)
	fmt.Println(content)

	// In Go, you won't have the equivalent of "global", so you'd need
	// to manage the loaded content differently if needed.
}

func executeFunction() {
	if targetFunction.IsValid() && len(targetArgs) > 0 {
		fmt.Println("Executing function...")
		result := targetFunction.Call(targetArgs)
		fmt.Println("Result:", result)
		targetFunction = reflect.Value{}
		targetArgs = nil
	}
}

func main() {
	// Your main loop here
	for {
		executeFunction()
		// Sleep for a while to avoid consuming too much CPU
		time.Sleep(1 * time.Second)
	}
}
