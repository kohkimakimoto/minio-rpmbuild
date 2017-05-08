#!/usr/bin/env bash
set -e

if [ -z "$DOCKER_IMAGE" ]; then
    # Get the directory path.
    SOURCE="${BASH_SOURCE[0]}"
    while [ -h "$SOURCE" ] ; do SOURCE="$(readlink "$SOURCE")"; done
    repo_dir="$( cd -P "$( dirname "$SOURCE" )/" && pwd )"

    # Move the repository directory
    cd "$repo_dir"

    rm -rf SOURCES/minio
    rm -rf SOURCES/minio-client
    
    cd SOURCES
    curl -L -o minio https://dl.minio.io/server/minio/release/linux-amd64/archive/minio.RELEASE.2017-05-05T01-14-51Z
    chmod +x minio
    # see https://github.com/minio/mc/issues/873
    curl -L -o minio-client https://dl.minio.io/client/mc/release/linux-amd64/archive/mc.RELEASE.2017-04-03T18-35-01Z
    chmod +x minio-client
    cd -

    echo "Building RPM packages..."
    for image in 'kohkimakimoto/rpmbuild:el7'; do
        docker run \
            --env DOCKER_IMAGE=${image}  \
            -v $repo_dir:/tmp/repo \
            -w /tmp/repo \
            --rm \
            ${image} \
            bash ./build.sh
    done

    exit 0
fi

echo "Building RPM in '$DOCKER_IMAGE' container..."

repo_dir=$(pwd)
platform=el${RHEL_VERSION}
subver=$(./SOURCES/minio version | grep Version | awk '{print $2}' | sed -e 's/[^0-9]//g')

cp -pr SPECS $HOME/rpmbuild/
cp -pr SOURCES $HOME/rpmbuild/

cd $HOME
rpmbuild \
    --define "_subver ${subver}" \
    --define "_rhel_version ${RHEL_VERSION}" \
    -ba rpmbuild/SPECS/minio.spec

echo "Copying generated files to the shared folder..."
cd $repo_dir

mkdir -p dist/${platform}
cp -pr $HOME/rpmbuild/RPMS dist/${platform}
cp -pr $HOME/rpmbuild/SRPMS dist/${platform}
