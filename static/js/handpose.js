import React, { useEffect, useRef } from 'react';
        import { Hands, HAND_CONNECTIONS } from '@mediapipe/hands';
        import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils';
        

        const MyComponent = () => {
        const videoRef = useRef(null);
        const landmarksContainerRef = useRef(null);

        useEffect(() => {
        const pose = new Pose({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
        });
        pose.setOptions({
            modelComplexity: 1,
            smoothLandmarks: true,
            enableSegmentation: false,
            smoothSegmentation: true,
            minDetectionConfidence: 0.3,
            minTrackingConfidence: 0.3,
        });

        pose.onResults(handleResults);

        function handleResults(results) {
            if (results.poseLandmarks) {
            const landmarksCanvas = document.getElementById('hand-landmarks-canvas');
            const canvasContext = landmarksCanvas.getContext('2d');
            canvasContext.clearRect(0, 0, landmarksCanvas.width, landmarksCanvas.height);
            drawConnectors(canvasContext, results.poseLandmarks, HAND_CONNECTIONS, { color: '#00FF00', lineWidth: 5 });
            drawLandmarks(canvasContext, results.poseLandmarks, { color: '#FF0000', lineWidth: 2 });
            }
        }

        const camera = new Camera(video, {
            onFrame: async () => {
            await pose.send({ image: video });
            },
            width: 640,
            height: 480,
        });
        camera.start();

        return () => {
            camera.stop();
            pose.close();
        };
        }, []);

        return (
            <div>
            <video ref={videoRef} width="640" height="480" />
            <div ref={landmarksContainerRef} className="landmarks-container" />
            </div>
        );
        };

        export default MyComponent;