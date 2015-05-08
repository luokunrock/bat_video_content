#!/bin/sh
setyamienv()
{
    if [ -n "$1" ]; then
        export YAMI_ROOT_DIR=$1
    else
        export YAMI_ROOT_DIR="/opt/yami"
    fi

    export VAAPI_PREFIX="${YAMI_ROOT_DIR}/vaapi"
    export LIBYAMI_PREFIX="${YAMI_ROOT_DIR}/libyami"
    export OMXCOMPONENT_PREFIX="${YAMI_ROOT_DIR}/omx"
    export GSTOMX_PREFIX="${YAMI_ROOT_DIR}/gst-omx"

    ADD_PKG_CONFIG_PATH="${VAAPI_PREFIX}/lib/pkgconfig/:${LIBYAMI_PREFIX}/lib/pkgconfig/:${OMXCOMPONENT_PREFIX}/lib/pkgconfig/"
    ADD_LD_LIBRARY_PATH="${VAAPI_PREFIX}/lib/:${LIBYAMI_PREFIX}/lib/:${OMXCOMPONENT_PREFIX}/lib/"
    ADD_PATH="${VAAPI_PREFIX}/bin/"

    PLATFORM_ARCH_64=`uname -a | grep x86_64`
    if [ -n "$PKG_CONFIG_PATH" ]; then
        export PKG_CONFIG_PATH="${ADD_PKG_CONFIG_PATH}:$PKG_CONFIG_PATH"
    elif [ -n "$PLATFORM_ARCH_64" ]; then
        export PKG_CONFIG_PATH="${ADD_PKG_CONFIG_PATH}:/usr/lib/pkgconfig/:/usr/lib/i386-linux-gnu/pkgconfig/"
    else 
        export PKG_CONFIG_PATH="${ADD_PKG_CONFIG_PATH}:/usr/lib/pkgconfig/:/usr/lib/x86_64-linux-gnu/pkgconfig/"
    fi
    
    export LD_LIBRARY_PATH="${ADD_LD_LIBRARY_PATH}:$LD_LIBRARY_PATH"

    export PATH="${ADD_PATH}:$PATH"

    export GST_PLUGIN_PATH_1.0="${GSTOMX_PREFIX}/lib/gstreamer-1.0"

    echo "*======================current configuration============================="
    echo "* VAAPI_PREFIX:               $VAAPI_PREFIX"
    echo "* LIBYAMI_PREFIX:             ${LIBYAMI_PREFIX}"
    echo "* LD_LIBRARY_PATH:            ${LD_LIBRARY_PATH}"
    echo "* PATH:                       $PATH"
    echo "*========================================================================="

    echo "* vaapi:     git clean -dxf && ./autogen.sh --prefix=\$VAAPI_PREFIX && make -j8 && make install"
    echo "* ffmpeg:    git clean -dxf && ./configure --prefix=\$VAAPI_PREFIX && make -j8 && make install"
    echo "* libyami:   git clean -dxf && ./autogen.sh --prefix=\$LIBYAMI_PREFIX --enable-tests --enable-tests-gles && make -j8 && make install"
}

setyamienv $1
currentscriptpath=$(cd "$(dirname "$0")"; pwd)
${currentscriptpath}/control.py
