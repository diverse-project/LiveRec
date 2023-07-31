#include <dlfcn.h>

void* current_lib;

void load_lib(char *lib_name) {
    current_lib = dlopen(lib_name, RTLD_NOW);
}

void close_lib() {
    dlclose(current_lib);
}

int main() {
    while (1)
    {
        //do nothing
    }
    return 0;
}