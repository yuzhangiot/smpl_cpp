﻿#ifndef OPENPOSE_EXPERIMENTAL_3D_RENDERER_HPP
#define OPENPOSE_EXPERIMENTAL_3D_RENDERER_HPP

#include <mutex>
#include <stdio.h>
#include <GL/glew.h>

#include <GL/gl.h>
#include <GL/glut.h>
#include <GL/freeglut_ext.h>
#include <GL/freeglut_std.h>
#include <GL/glu.h>
#include <opencv2/opencv.hpp>
#include <chrono>
#include <thread>
#include <fstream>
#include <mutex>
#include <functional>
#include <eigen3/Eigen/Eigen>
#include <iostream>
using namespace std;
#define BUFFER_OFFSET(i) ((char *)NULL + (i))

namespace op
{
    struct OBJObject;
    struct OBJFace;
    struct OBJVertex;
    struct OBJNormal;
    struct OBJTexture;
    struct OBJFaceItem;
    struct OBJMaterial;
    struct Vertex;

    class WObject
    {
    public:
        const static int RENDER_NORMAL = 0;
        const static int RENDER_POINTS = 1;
        const static int RENDER_WIREFRAME = 2;

        WObject();
        ~WObject();
        bool clearOBJFile(bool clearObject = true);
        void print();
        bool loadOBJFile( const std::string& data_path, const std::string& mesh_filename, const std::string& material_filename );
        bool loadEigenData(const Eigen::MatrixXf& v, const Eigen::MatrixXf& f);
        void render();
        void rebuild(int renderType = WObject::RENDER_NORMAL, float param = 1);
        void rebuildVArr(int renderType = WObject::RENDER_NORMAL, float param = 1);

    private:
        std::string mDataPath;
        std::string mCurrentMaterial;
        std::shared_ptr<OBJObject> mObject;
        std::map<std::string,GLuint> textures;
        GLuint vao;
        GLuint vbuffer;
        GLuint listId;
        GLuint ibuffer;
        GLuint getTexture(const std::string& filename);
        bool releaseTexture(const std::string& filename);
        bool loadTexture(const std::string& filename, bool clamp);
        void processMaterialLine( const std::string& line );
        void processMeshLine( const std::string& line );
    };

    // This worker will do 3-D rendering
    class  WRender3D
    {
    public:
        std::mutex renderMutex;

        WRender3D();

        ~WRender3D();

        void initializationOnThread();

        void workOnThread();

        void addObject(std::shared_ptr<WObject> wObject);

    };
}

#endif // OPENPOSE_EXPERIMENTAL_3D_RENDERER_HPP
