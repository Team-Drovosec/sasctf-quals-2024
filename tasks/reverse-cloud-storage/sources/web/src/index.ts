import { FreeCamera } from "@babylonjs/core/Cameras/freeCamera";
import { WebGPUEngine } from "@babylonjs/core/Engines/webgpuEngine";
import { Matrix, Vector3, Vector4 } from "@babylonjs/core/Maths/math.vector";
import { CreateBox } from "@babylonjs/core/Meshes/Builders/boxBuilder";
import "@babylonjs/core/Meshes/thinInstanceMesh";
import { Scene } from "@babylonjs/core/scene";
import { HemisphericLight } from "@babylonjs/core/Lights/hemisphericLight";
import { ShaderMaterial } from "@babylonjs/core/Materials/shaderMaterial";
import { ShaderLanguage } from "@babylonjs/core/Materials/shaderLanguage";
import { ShaderStore } from "@babylonjs/core/Engines/shaderStore";
import { Scalar, PBRMaterial, DynamicTexture, StandardMaterial } from "@babylonjs/core";
import { ISceneLoaderPluginFactory, SceneLoader } from "@babylonjs/core/Loading/sceneLoader";
import sceneGlb from "../assets/scene.glb";
import { GLTFFileLoader } from "@babylonjs/loaders/glTF";


function modPow(expo: bigint, base: bigint, p: bigint): number {
    let x = BigInt(base) % p, res = expo & 1n? x: 1n
    do {
        x = x**2n % p
        if (expo & 2n) res = res * x % p
    } while (expo /= 2n)
    return Number(res)
}

await (async () => {
    (SceneLoader.GetPluginForExtension(".glb") as ISceneLoaderPluginFactory).createPlugin = () => {
        const loader = new GLTFFileLoader();
        loader.useSRGBBuffers = false;
        return loader;
    };
    const canvas = document.querySelector("#target") as HTMLCanvasElement;
    const engine = new WebGPUEngine(canvas);
    await engine.initAsync();

    const resizeWatcher = new ResizeObserver(() => {
        engine.resize();
    });
    resizeWatcher.observe(canvas);

    const scene = new Scene(engine);
    new HemisphericLight("HemiLight", new Vector3(0, 1, 0), scene);
    await SceneLoader.AppendAsync("./", sceneGlb, scene);

    const textureScreen = new DynamicTexture("dynamic texture", {width:1024, height:512}, scene);
	const materialScreen = new StandardMaterial("Mat", scene);    				
	materialScreen.diffuseTexture = textureScreen;
    scene.getMeshById("screen").material = materialScreen;
    
    let prevDownloadProgress = -1;
    const SetDownloadProgress = (x: number) => {
        const progress = Math.round(x * 100);
        if (progress != prevDownloadProgress) {
            const cells = 25;
            const filledCells = Math.round(cells * x);
            const lines = [
                "$ wget https://cloud/task &&",
                "./task",
                `${progress}%[${"=".repeat(Math.max(filledCells-1, 0))}>${" ".repeat(cells-filledCells)}]`,
            ];
            if (progress == 100) {
                lines.push("Enter password: ");
            }
            const ctx = textureScreen.getContext();
            const size = textureScreen.getSize();
            ctx.beginPath();
            ctx.fillStyle = "#000000";
            ctx.fillRect(0, 0, size.width, size.height);
            ctx.font = "bold 60px monospace";
            ctx.fillStyle = "#33FF33";
            for (const [i, line] of lines.entries()) {
                ctx.fillText(line, 10, 100 + 80 * i);
            }
            textureScreen.update(false);
            prevDownloadProgress = progress;
        }
    };
    SetDownloadProgress(0);

    const camera = new FreeCamera("camera1", new Vector3(2, 3, 5), scene);
    camera.inputs.clear();
    camera.inputs.addMouse();
    camera.inputs.addTouch();
    camera.setTarget(new Vector3(4, 2.5, -6));
    camera.attachControl(canvas, true);
    {
        let isLocked = false;
        scene.onPointerDown = function (evt) {
            if (!isLocked) {
                canvas.requestPointerLock = canvas.requestPointerLock || canvas.msRequestPointerLock || canvas.mozRequestPointerLock || canvas.webkitRequestPointerLock;
                if (canvas.requestPointerLock) {
                    canvas.requestPointerLock();
                }
            }
        };
        const pointerlockchange = function () {
            const doc = document as any;
            const controlEnabled = doc.mozPointerLockElement || doc.webkitPointerLockElement || doc.msPointerLockElement || doc.pointerLockElement || null;
            
            if (!controlEnabled) {
                isLocked = false;
            } else {
                isLocked = true;
            }
        };

        document.addEventListener("pointerlockchange", pointerlockchange, false);
        document.addEventListener("mspointerlockchange", pointerlockchange, false);
        document.addEventListener("mozpointerlockchange", pointerlockchange, false);
        document.addEventListener("webkitpointerlockchange", pointerlockchange, false);
    }

    {
        ShaderStore.ShadersStoreWGSL["cloudStorageVertexShader"]=`   
            #include<sceneUboDeclaration>
            #include<meshUboDeclaration>
            #include<instancesDeclaration>

            attribute position : vec3<f32>;
            attribute x: f32;

            flat varying x: u32;

            fn spiral(spiral_progress: f32) -> vec4f {
                let start_pos = vec3f(4,8,0);
                let final_pos = vec3f(4.9,1,-4.2);
                let theta: f32 = 50.0 * (1.0 - spiral_progress);
                let r: f32 = length(vec2<f32>(final_pos.x - start_pos.x, final_pos.z - start_pos.z)) * 0.5 * (1.0 - spiral_progress);
                
                return vec4f(
                    mix(start_pos.x, final_pos.x, spiral_progress) + r * cos(theta),
                    mix(start_pos.y, final_pos.y, spiral_progress),
                    mix(start_pos.z, final_pos.z, spiral_progress) + r * sin(theta),
                    0.0
                );
            }

            @vertex
            fn main(input : VertexInputs) -> FragmentInputs {
                #include<instancesVertex>
                let vert_pos = vec4<f32>(vertexInputs.position, 1.0);
                let world_pos = vec4f(finalWorld[3].xyz, 0.0);
                if input.x <= 0.6 {
                    vertexOutputs.position = scene.viewProjection * (vert_pos + mix(world_pos, spiral(0), input.x/0.6));
                } else {
                    vertexOutputs.position = scene.viewProjection * (vert_pos + spiral((input.x - 0.6) / 0.2));
                }
                vertexOutputs.x = input.instanceIndex * 2 + u32(min(floor((1 - input.x) * 4), 3));
            }
        `;
        // var<storage, read> test : array<u32>;
        // let byte = (u32(color1.x) % 4) + (u32(color1.y) % 4) * 4 + (u32(color2.y) % 4) * 16 + (u32(color2.z) % 4) * 64;
        // let byteNorm = f32(byte) / 255.0;
        // if byte == test[(input.x/2)] {
        //     fragmentOutputs.color = vec4f(1, 1, 1, 1);
        // } else {
        //     fragmentOutputs.color = vec4f(1, 0, 0, 1);
        // }
        ShaderStore.ShadersStoreWGSL["cloudStorageFragmentShader"]=`
            flat varying x: u32;
            var texture: texture_2d<f32>;

            @fragment
            fn main(input: FragmentInputs) -> FragmentOutputs {
                let size = textureDimensions(texture);
                let color1 = round(textureLoad(texture, vec2u(input.x % size.x, input.x / size.x), 0) * 255.0);
                let color2 = round(textureLoad(texture, vec2u((input.x+1) % size.x, (input.x + 1) / size.x), 0) * 255.0);
                let norm = f32((u32(color1.x) % 4) + (u32(color1.y) % 4) * 4 + (u32(color2.y) % 4) * 16 + (u32(color2.z) % 4) * 64) / 255.0;
                fragmentOutputs.color = vec4f(norm, norm, norm, 1);
            }
        `;
        const mat = new ShaderMaterial("shader", scene, 
            {
                vertex: "cloudStorage",
                fragment: "cloudStorage",
            },
            {
                attributes: ["position", "x"],
                uniformBuffers: ["Scene", "Mesh"],
                shaderLanguage: ShaderLanguage.WGSL,
            }
        );
        mat.setTexture("texture", (scene.getMeshById("gut").material as PBRMaterial).albedoTexture);

        const part = CreateBox("part", { width: 0.01, height: 0.01, depth: 0.01 }, scene);
        part.material = mat;
        
        const n = 367126;
        const nClouds = 100, nPoints = Math.floor(n / nClouds);
        const bufferMatrices = new Float32Array(16 * n);
        for(let cloud = 0; cloud < nClouds; ++cloud) {
            let xOffset = Scalar.RandomRange(-20, 20);
            let zOffset = Scalar.RandomRange(-20, 20);
            let yOffset = Scalar.RandomRange(15, 25);
            const spheres = Array.from(Array(Math.floor(Scalar.RandomRange(5, 20))).keys()).map(() => {
                const radius = Scalar.RandomRange(0.25, 1);
                return [
                    new Vector3(
                        Scalar.RandomRange(-2 + radius + xOffset, 2 - radius + xOffset),
                        Scalar.RandomRange(yOffset + radius, 2 - radius + yOffset),
                        Scalar.RandomRange(-2 + radius + zOffset, 2 - radius + zOffset)
                    ),
                    radius
                ];
            });
            for(let pointI = 0; pointI < nPoints + (cloud == nClouds - 1 ? n % nClouds : 0); ++pointI) {
                const point = (() => {
                    while(true) {
                        const point = new Vector3(
                            Scalar.RandomRange(-2 + xOffset, 2 + xOffset),
                            Scalar.RandomRange(yOffset, 2 + yOffset),
                            Scalar.RandomRange(-2 + zOffset, 2 + zOffset)
                        );
                        if ((() => {
                            for (const sphere of spheres) {
                                if (point.subtract(sphere[0] as Vector3).length() <= (sphere[1] as number)) {
                                    return true;
                                }
                            }
                            return false;
                        })()) {
                            return point;
                        }
                    }
                })();
                const matrix = Matrix.Translation(point.x, point.y, point.z);
                matrix.copyToArray(bufferMatrices, 16 * (cloud * nPoints + pointI));
            }
        }

        // const testBuffer = new StorageBuffer(engine, n * 4);
        // testBuffer.update(new Int32Array());
        // mat.setStorageBuffer("test", testBuffer);
        // const encData = new Int32Array([]);
        // const testData = new Int32Array([]);
        part.thinInstanceSetBuffer("matrix", bufferMatrices, 16);

        const progress = Array(n).fill(0);
        part.thinInstanceRegisterAttribute("x", 1);
        part.thinInstanceSetAttributeAt("x", 0, progress);

        let idx: Array<number> = [];
        for (let i = 0; i < n; ++i) {
            idx.push(modPow(BigInt(i+1), 1337n, BigInt(n + 1)) - 1);
            // console.assert(testData[i] == encData[idx[i]]);
        }

        let elapsed = 0;
        const readyTime = Scalar.RandomRange(60, 120);
        scene.onBeforeRenderObservable.add(() => {
            const globalProgress = Math.min(elapsed / readyTime, 1);
            SetDownloadProgress(globalProgress);

            for (let i = 0; i < n; ++i) {
                const x = idx[i];
                if (i <= n - 1 - 118) {
                    const sp = i / n;
                    progress[x] = Math.min(Math.max((globalProgress - sp) / (1 - sp), 0), 1);
                }
            }
            part.thinInstanceSetAttributeAt("x", 0, progress);
            elapsed += engine.getDeltaTime() / 1000;
        });
    }

    engine.runRenderLoop(() => {
        scene.render();
    });
})()
