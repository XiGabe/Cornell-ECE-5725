#!/bin/bash
# Build script for YOLO Hand Detection System
# Author: Hongxi Chen
# Date: 2025-12-09

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking dependencies..."

    # Check compiler
    if command_exists g++; then
        GCC_VERSION=$(g++ --version | head -n1)
        print_success "Found: $GCC_VERSION"
    else
        print_error "g++ compiler not found"
        exit 1
    fi

    # Check make
    if command_exists make; then
        MAKE_VERSION=$(make --version | head -n1)
        print_success "Found: $MAKE_VERSION"
    else
        print_error "make not found"
        exit 1
    fi

    # Check pkg-config
    if command_exists pkg-config; then
        print_success "Found: pkg-config"
    else
        print_warning "pkg-config not found, may cause library detection issues"
    fi

    # Check OpenCV
    if pkg-config --exists opencv4 2>/dev/null; then
        OPENCV_VERSION=$(pkg-config --modversion opencv4 2>/dev/null || echo "unknown")
        print_success "Found: OpenCV $OPENCV_VERSION"
    else
        print_error "OpenCV4 not found"
        print_status "Install with: sudo apt install libopencv-dev"
        exit 1
    fi

    # Check NCNN
    if [ -f "/usr/local/lib/ncnn/libncnn.a" ] || ldconfig -p | grep -q libncnn; then
        print_success "Found: NCNN library"
    else
        print_warning "NCNN not found in standard paths"
        print_status "YOLO detection may not work properly"
    fi

    # Check WiringPi
    if ldconfig -p | grep -q libwiringPi; then
        print_success "Found: WiringPi library"
    else
        print_warning "WiringPi not found"
        print_status "Motor control may not work properly"
        print_status "Install with: sudo apt install wiringpi"
    fi
}

# Function to clean previous build
clean_build() {
    print_status "Cleaning previous build..."
    if command_exists make; then
        make clean-all >/dev/null 2>&1 || true
    fi
    print_success "Build directory cleaned"
}

# Function to build the project
build_project() {
    local build_type=${1:-release}

    print_status "Building project ($build_type mode)..."

    # Set build type flags
    case $build_type in
        "debug")
            make debug
            ;;
        "release")
            make release
            ;;
        "test")
            make test
            ;;
        *)
            make
            ;;
    esac

    if [ $? -eq 0 ]; then
        print_success "Build completed successfully"
    else
        print_error "Build failed"
        exit 1
    fi
}

# Function to run tests
run_tests() {
    print_status "Running tests..."

    # Check if test binary exists
    if [ -f "bin/test_omni" ]; then
        print_status "Motor control test available"
        print_warning "Make sure robot is safely supported before running tests"

        read -p "Run motor test? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            make run-test
        fi
    else
        print_warning "No test binary found"
    fi
}

# Function to show build summary
build_summary() {
    print_status "Build Summary:"
    echo "================================"

    # Show project info
    if command_exists make; then
        make info 2>/dev/null || print_warning "Could not show project info"
    fi

    echo
    print_status "Available executables:"
    [ -f "bin/main" ] && echo "  ✓ bin/main - Main application"
    [ -f "bin/test_omni" ] && echo "  ✓ bin/test_omni - Motor test program"

    echo
    print_status "Next steps:"
    echo "  1. Run main application: make run"
    echo "  2. Access web interface: http://<your-ip>:8080"
    echo "  3. Test motors: make run-test"
    echo "  4. View help: make help"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help      Show this help message"
    echo "  -c, --clean     Clean build directory only"
    echo "  -d, --debug     Build in debug mode"
    echo "  -r, --release   Build in release mode (default)"
    echo "  -t, --test      Build tests only"
    echo "  --no-check      Skip dependency check"
    echo "  --no-tests      Skip running tests after build"
    echo "  -v, --verbose   Verbose output"
    echo ""
    echo "Examples:"
    echo "  $0                # Build in release mode"
    echo "  $0 -d             # Build in debug mode"
    echo "  $0 -c             # Clean only"
    echo "  $0 -t             # Build tests"
}

# Main script execution
main() {
    local build_type="release"
    local check_deps=true
    local run_tests_after=true
    local clean_only=false
    local verbose=false

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -c|--clean)
                clean_only=true
                shift
                ;;
            -d|--debug)
                build_type="debug"
                shift
                ;;
            -r|--release)
                build_type="release"
                shift
                ;;
            -t|--test)
                build_type="test"
                run_tests_after=false
                shift
                ;;
            --no-check)
                check_deps=false
                shift
                ;;
            --no-tests)
                run_tests_after=false
                shift
                ;;
            -v|--verbose)
                verbose=true
                set -x  # Enable command tracing
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # Print banner
    echo "======================================"
    echo "  YOLO Hand Detection Build Script"
    echo "======================================"
    echo ""

    # Change to script directory
    cd "$(dirname "$0")/.."

    # Check dependencies
    if [ "$check_deps" = true ]; then
        check_dependencies
        echo ""
    fi

    # Clean only
    if [ "$clean_only" = true ]; then
        clean_build
        print_success "Clean completed"
        exit 0
    fi

    # Clean and build
    clean_build
    echo ""
    build_project "$build_type"

    # Run tests
    if [ "$run_tests_after" = true ] && [ "$build_type" != "test" ]; then
        echo ""
        run_tests
    fi

    echo ""
    build_summary

    print_success "Build script completed successfully!"
}

# Run main function with all arguments
main "$@"