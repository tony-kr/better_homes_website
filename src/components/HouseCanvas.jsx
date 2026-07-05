import { motion, useTransform, useSpring } from 'framer-motion';
import { useEffect, useState } from 'react';
import './HouseCanvas.css';

const HouseCanvas = ({ activeSection }) => {
    // Sketch vs full house driven by active section (landing = sketch, others = full house)
    const showSketch = activeSection === 'landing';

    // Zoom/Pan controls based on active section
    const [viewState, setViewState] = useState({ scale: 1.3, x: 20, y: 0, opacity: 1, livingRoomOpacity: 0 });

    useEffect(() => {
        switch (activeSection) {
            case 'landing':
                setViewState({ scale: 1.3, x: 20, y: 0, opacity: 1, livingRoomOpacity: 0 });
                break;
            case 'hero':
                // Zoom closer, house VISIBLE
                setViewState({ scale: 4, x: 20, y: 0, opacity: 1, livingRoomOpacity: 0 });
                break;
            case 'living-room':
                // Zoom into living room area, keep house visible
                setViewState({ scale: 8, x: 20, y: 25, opacity: 1, livingRoomOpacity: 0 });
                break;
            case 'kitchen':
                // Middle Left
                setViewState({ scale: 3, x: 20, y: 0, opacity: 1, livingRoomOpacity: 0 });
                break;
            case 'bedroom':
                // Top area
                setViewState({ scale: 3, x: -10, y: -30, opacity: 1, livingRoomOpacity: 0 });
                break;
            case 'patio':
                // Bottom Right
                setViewState({ scale: 2.5, x: -20, y: 20, opacity: 1, livingRoomOpacity: 0 });
                break;
            default:
                setViewState({ scale: 1.3, x: 20, y: 0, opacity: 1, livingRoomOpacity: 0 });
        }
    }, [activeSection]);

    // Smooth transitions for camera movement
    // Looser spring for visible movement
    const springConfig = { stiffness: 50, damping: 20, mass: 1 };
    const scale = useSpring(viewState.scale, springConfig);
    const x = useSpring(viewState.x, springConfig);
    const y = useSpring(viewState.y, springConfig);
    const opacity = useSpring(viewState.opacity, springConfig);

    return (
        <div className="house-canvas-container">
            {/* Living Room Photo Layer - Fixed Background */}
            <motion.div
                className="room-photo-layer"
                initial={{ opacity: 0, scale: 1.1 }}
                animate={{
                    opacity: viewState.livingRoomOpacity,
                    scale: viewState.livingRoomOpacity > 0 ? 1 : 1.1
                }}
                transition={{ duration: 1.5, ease: "easeInOut", delay: 0.8 }} // Delayed to show house zoom first
            >
                <img src="/living_room.jpg" alt="Living Room" />
            </motion.div>

            <div className="house-canvas-inner">
                <motion.div
                    className="house-transform-wrapper"
                    animate={{ rotateY: [-5, 5] }}
                    transition={{
                        duration: 5,
                        repeat: Infinity,
                        repeatType: "reverse",
                        ease: "easeInOut"
                    }}
                    style={{
                        scale,
                        x: useTransform(x, val => `${val}%`),
                        y: useTransform(y, val => `${val}%`),
                        opacity
                    }}
                >
                    {/* Sketch Layer */}
                    <motion.div
                        className="house-layer sketch"
                        animate={{ opacity: showSketch ? 1 : 0 }}
                        transition={{ duration: 1, ease: "easeInOut" }}
                    >
                        <img src="/line_sketch.svg" alt="House Sketch" />
                    </motion.div>

                    {/* Full House Layer */}
                    <motion.div
                        className="house-layer full"
                        animate={{ opacity: showSketch ? 0 : 1 }}
                        transition={{ duration: 1, ease: "easeInOut" }}
                    >
                        <img src="/full_house.svg" alt="Full House" />
                    </motion.div>
                </motion.div>
            </div>
        </div>
    );
};

export default HouseCanvas;
