import shutil
import os
from conans.tools import download, unzip, check_md5, check_sha1, check_sha256
from conans import ConanFile, CMake, tools


class ConfuMagnumIntegrationConan(ConanFile):
    name = "magnum-integration"
    license = "BSL-1.0"
    author = "werto87"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "magnum integration is used to add libs to magnum"
    topics = ("magnum")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_emscripten_pthreads": [True, False],
        "with_bullet": [True, False],
        "with_dar": [True, False],
        "with_glm": [True, False],
        "with_imgui": [True, False],
        "build_tests": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": False,
        "with_emscripten_pthreads": True,
        "with_bullet": False,
        "with_dar": False,
        "with_glm": False,
        "with_imgui": True,
        "build_tests": False,
    }
    generators = "cmake"
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("magnum/2020.06@werto87/stable")
        self.requires("imgui/1.82@werto87/stable")

    def source(self):
        git = tools.Git(folder=self._source_subfolder)
        git.clone("https://github.com/mosra/magnum-integration.git", "master")

    def _configure_cmake(self):
        cmake = CMake(self)

        def add_cmake_option(option, value):
            var_name = "{}".format(option).upper()
            value_str = "{}".format(value)
            var_value = "ON" if value_str == 'True' else "OFF" if value_str == 'False' else value_str
            cmake.definitions[var_name] = var_value
            print("{0}={1}".format(var_name, var_value))
        for option, value in self.options.items():
            add_cmake_option(option, value)
        add_cmake_option("BUILD_STATIC", not self.options.shared)
        add_cmake_option(
            "BUILD_STATIC_PIC", not self.options.shared and self.options.get_safe("fPIC") == True)
        add_cmake_option("LIB_SUFFIX", "")
        corradeRoot = self.deps_cpp_info["corrade"].rootpath
        magnumRoot = self.deps_cpp_info["magnum"].rootpath
        imguiRoot = self.deps_cpp_info["imgui"].rootpath
        imguiSrc = imguiRoot.split("/package/")[0]+"/source"
        corradeSrc = corradeRoot.split("/package/")[0]+"/source"
        cmake.definitions["CMAKE_FIND_ROOT_PATH"] = "/"
        cmake.definitions["CORRADE_INCLUDE_DIR"] = corradeRoot + "/include"
        cmake.definitions["_CORRADE_CONFIGURE_FILE"] = corradeRoot + \
            "/include/Corrade/"
        cmake.definitions["_CORRADE_CONTAINERS_INCLUDE_DIR"] = corradeRoot + "/include"
        cmake.definitions["CORRADE_UTILITY_LIBRARY_DEBUG"] = corradeRoot + "/include"
        cmake.definitions["CORRADE_UTILITY_LIBRARY_RELEASE"] = corradeRoot + "/include"
        cmake.definitions["_CORRADE_UTILITY_INCLUDE_DIR"] = corradeRoot + "/include"
        cmake.definitions["MAGNUM_INCLUDE_DIR"] = self.deps_cpp_info["magnum"].rootpath + "/include"
        cmake.definitions["_MAGNUM_CONFIGURE_FILE"] = self.deps_cpp_info["magnum"].rootpath + "/include"
        cmake.definitions["_CORRADE_MODULE_DIR"] = f"{corradeSrc}/source_subfolder/modules/"
        cmake.definitions["_MAGNUM_MODULE_DIR"] = f"{corradeSrc}/source_subfolder/modules/"
        cmake.definitions["CMAKE_LIBRARY_PATH"] = f"{corradeRoot}/lib/;{magnumRoot}/lib/"
        cmake.definitions["CMAKE_PROGRAM_PATH"] = f"{corradeRoot};{magnumRoot}"
        cmake.definitions["CMAKE_SYSTEM_PREFIX_PATH"] = f"{corradeRoot};{magnumRoot}"
        cmake.definitions["CMAKE_INCLUDE_PATH"] = f"{corradeRoot};{magnumRoot}"
        cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type
        cmake.definitions["IMGUI_DIR"] = f"{imguiSrc}/source_subfolder/"
        if self.settings.os == "Emscripten":
            cmake.definitions["CORRADE_TARGET_EMSCRIPTEN"] = True
            cmake.definitions["MAGNUM_TARGET_EMSCRIPTEN"] = True
            if self.options.with_emscripten_pthreads:
                cmake.definitions["CMAKE_CXX_FLAGS"] = "-s USE_PTHREADS"
                cmake.definitions["CMAKE_EXE_LINKER_FLAGS"] = "-s USE_PTHREADS"
        cmake.configure(source_folder=self._source_subfolder)
        cmake.definitions["CMAKE_MODULE_PATH"] = "/home/walde/emsdk/upstream/emscripten/cmake/Modules/FindOpenGL.cmake"

        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        if self.settings.build_type == "Debug":
            self.cpp_info.libs = ["MagnumImGuiIntegration-d"]
        else:
            self.cpp_info.libs = ["MagnumImGuiIntegration"]
