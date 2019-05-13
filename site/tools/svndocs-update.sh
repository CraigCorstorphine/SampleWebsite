#!/bin/bash

echo $(date -u)
export PATH=/usr/local/bin:$PATH

variant="$1"
if [ "x$variant" = "x" ]; then
    echo "Missing parameter: variant"
    exit 1
fi

case "x$variant" in
    xtrunk)
        publishdocs=svndocs
        ;;
    x1.9.x)
        publishdocs=svndocs-1.9
        ;;
    x1.8.x)
        publishdocs=svndocs-1.8
        ;;
    *)
        echo "Bad variant: $variant"
        exit 1
        ;;
esac

docdir=$HOME/svndocs-$variant
docsrc=$docdir/working
docbuild=$docdir/build
docversion=$docdir/last-version
docpublish=$HOME/public_html/$publishdocs

set -e
set -x

svn update $docsrc --non-interactive >/dev/null

if [ -f $docversion ]
then
    oldver=$(cat $docversion)
else
   oldver=
fi
newver=$(svn info $docsrc | grep ^Revision:)

if [ "x$newver" = "x$oldver" ]
then
    exit 0
fi

cd $docsrc
./autogen.sh >/dev/null
rm -fr $docbuild
mkdir $docbuild
cd $docbuild
$docsrc/configure --prefix=$docbuild/inst --with-lz4=internal --with-utf8proc=internal >/dev/null

make doc-api > $docdir/doc-api.log 2>&1
# FIXME: JavHL do build is currently 'orribly broken.
set +e
make doc-javahl > $docdir/doc-javahl.log 2>&1
set -e

mv $docbuild/doc/doxygen/html $docbuild/doc/capi
mv $docbuild/doc/javadoc $docbuild/doc/javahl
cp $docdir/doc-api.log $docbuild/doc/capi.build.log
cp $docdir/doc-javahl.log $docbuild/doc/javahl.build.log
rmdir $docbuild/doc/doxygen

if [ -d $docpublish ]; then
    mv $docpublish $docpublish.$$
fi
mv $docbuild/doc $docpublish
rm -fr $docpublish.$$
echo $newver > $docversion
