"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { Canvas, ThreeEvent, useFrame } from "@react-three/fiber";
import { Environment, Lightformer, useGLTF } from "@react-three/drei";
import { NeutralToneMapping, type Group } from "three";
import Image from "next/image";

export type CopieState = "idle" | "listening" | "thinking" | "responding" | "success";

export type CopieProps = {
  state?: CopieState;
  onInteract?: () => void;
  className?: string;
  label?: string;
};

const MODEL_URL = "/models/copie-mascot-web.glb";
// The model stands on y = 0 and is ~4.13 units tall; this centres it in view.
const BASE_Y = -2.07;

function Model({ state, onInteract, reducedMotion }: Required<Pick<CopieProps, "state">> & {
  onInteract?: () => void;
  reducedMotion: boolean;
}) {
  const { scene } = useGLTF(MODEL_URL);
  const group = useRef<Group>(null);
  const pointer = useRef({ x: 0, y: 0 });
  const hover = useRef(false);

  useFrame(({ clock }, delta) => {
    if (!group.current) return;
    const t = clock.elapsedTime;
    const ease = Math.min(1, delta * 6);
    const lookX = hover.current ? pointer.current.x * 0.12 : 0;
    const lookY = hover.current ? pointer.current.y * 0.06 : 0;
    const tilt = state === "thinking" ? -0.075 : state === "listening" ? 0.045 : 0;
    group.current.rotation.y += (lookX - group.current.rotation.y) * ease;
    group.current.rotation.z += (tilt - group.current.rotation.z) * ease;
    group.current.rotation.x += (lookY - group.current.rotation.x) * ease;
    if (reducedMotion) {
      group.current.position.y = BASE_Y;
      return;
    }
    const bounce = state === "success" ? Math.abs(Math.sin(t * 7)) * 0.19 : 0;
    const speaking = state === "responding" ? Math.sin(t * 9) * 0.025 : 0;
    const thinking = state === "thinking" ? Math.sin(t * 3) * 0.04 : 0;
    group.current.position.y = BASE_Y + Math.sin(t * 1.6) * 0.035 + bounce + speaking + thinking;
  });

  function move(event: ThreeEvent<PointerEvent>) {
    pointer.current.x = Math.max(-1, Math.min(1, event.point.x / 2));
    pointer.current.y = Math.max(-1, Math.min(1, event.point.y / 2));
  }

  return (
    <group
      ref={group}
      position={[0, BASE_Y, 0]}
      onPointerMove={move}
      onPointerOver={() => { hover.current = true; document.body.style.cursor = "pointer"; }}
      onPointerOut={() => { hover.current = false; document.body.style.cursor = ""; }}
      onClick={(event) => { event.stopPropagation(); onInteract?.(); }}
    >
      <primitive object={scene} />
    </group>
  );
}

/** 3D COPIE with a static image fallback for devices without WebGL. */
export function Copie({ state = "idle", onInteract, className = "", label = "COPIE", }: CopieProps) {
  const [webGL, setWebGL] = useState<boolean | null>(null);
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const canvas = document.createElement("canvas");
    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReducedMotion(query.matches);
    const frame = window.requestAnimationFrame(() => {
      setWebGL(Boolean(canvas.getContext("webgl2") || canvas.getContext("webgl")));
      update();
    });
    query.addEventListener("change", update);
    return () => {
      window.cancelAnimationFrame(frame);
      query.removeEventListener("change", update);
    };
  }, []);

  return (
    <div
      className={`relative h-full min-h-72 w-full ${className}`}
      role={onInteract ? "button" : "img"}
      tabIndex={onInteract ? 0 : undefined}
      aria-label={label}
      onKeyDown={(event) => {
        if (onInteract && (event.key === "Enter" || event.key === " ")) {
          event.preventDefault();
          onInteract();
        }
      }}
    >
      {webGL ? (
        <Canvas
          camera={{ position: [0, 0, 9.5], fov: 35 }}
          dpr={[1, 1.75]}
          gl={{ alpha: true, antialias: true, toneMapping: NeutralToneMapping }}
        >
          {/* Soft studio lighting matched to the Blender reference render. */}
          <hemisphereLight args={["#ffffff", "#cfc9c6", 0.9]} />
          <directionalLight position={[-3.2, 4.6, 7]} intensity={2.6} />
          <directionalLight position={[4.5, 2.2, 6]} intensity={0.95} color="#f2f6ff" />
          <directionalLight position={[1.5, 6, -5]} intensity={1.0} />
          {/* Procedural environment (no HDR download) for the laptop metal and glossy headset. */}
          <Environment resolution={128} frames={1}>
            <Lightformer form="rect" intensity={1.6} position={[-4, 5, 6]} scale={[8, 6, 1]} />
            <Lightformer form="rect" intensity={0.9} position={[5, 1, 5]} scale={[6, 8, 1]} />
            <Lightformer form="rect" intensity={1.1} position={[0, 6, -6]} scale={[10, 4, 1]} />
            <Lightformer form="rect" intensity={0.4} position={[0, -5, 2]} scale={[10, 3, 1]} />
          </Environment>
          <Suspense fallback={null}>
            <Model state={state} onInteract={onInteract} reducedMotion={reducedMotion} />
          </Suspense>
        </Canvas>
      ) : (
        <Image
          src="/mascot/copie-front-laptop.png"
          alt=""
          fill
          className="object-contain"
          sizes="(max-width: 768px) 100vw, 500px"
          priority
        />
      )}
    </div>
  );
}

useGLTF.preload(MODEL_URL);
