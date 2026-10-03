// ตารางรายวิชา — ม็อกอัพ 07-course-table
// เดสก์ท็อปเป็นตารางเรียงคอลัมน์ได้ มือถือเป็นรายการการ์ด
// คลิกแถวเพื่อดูรายละเอียดวิชาใต้ตาราง ปิดท้ายด้วยแถบรวมหน่วยกิตตัวเลขใหญ่
"use client";

import { useState } from "react";
import { ArrowLeft, BarChart3, ChevronDown, ChevronRight, FileText, Info } from "lucide-react";
import { motion } from "motion/react";
import type { Course, CourseTableData } from "@/types/contract";

type SortKey = "code" | "name_th" | "credits" | "category";
type SortDirection = "asc" | "desc";

const COLUMNS: { key: SortKey; label: string; align: "left" | "right" }[] = [
  { key: "code", label: "รหัส", align: "left" },
  { key: "name_th", label: "รายวิชา", align: "left" },
  { key: "credits", label: "หน่วยกิต", align: "right" },
  { key: "category", label: "หมวด", align: "left" },
];

export function CourseTable({
  data,
  disabled = false,
  animate = true,
}: {
  data: CourseTableData;
  disabled?: boolean;
  animate?: boolean;
}) {
  const [sort, setSort] = useState<{ key: SortKey; direction: SortDirection } | null>(null);
  const [selected, setSelected] = useState<string | null>(data.courses[1]?.code ?? data.courses[0]?.code ?? null);

  const courses = sort ? sortCourses(data.courses, sort.key, sort.direction) : data.courses;
  const selectedCourse = courses.find((course) => course.code === selected) ?? null;

  const toggleSort = (key: SortKey) =>
    setSort((current) =>
      current?.key === key && current.direction === "asc" ? { key, direction: "desc" } : { key, direction: "asc" },
    );

  const toggleRow = (code: string) => setSelected((current) => (current === code ? null : code));

  const heading = `รายวิชา ปี ${data.year} เทอม ${data.semester}`;

  if (data.courses.length === 0) {
    return (
      <section className="flex flex-col gap-4 rounded-2xl border border-[#d2e0f5] bg-white/95 p-6 shadow-sm" aria-label={heading}>
        <div className="flex items-center gap-2">
          <span className="size-2 bg-[#155ff2]" />
          <span className="font-label text-xs font-bold tracking-[0.2em] text-[#155ff2] uppercase">
            AI RESPONSE
          </span>
        </div>
        <h2 className="copie-heading font-display text-2xl font-black italic text-[#080b12]">
          {heading}
        </h2>
        <p className="rounded-xl border border-[#d2e0f5] bg-slate-50 px-4 py-6 text-center text-[#6b82a6]">
          ไม่พบรายวิชาของปีและเทอมนี้ในเล่มหลักสูตร
        </p>
      </section>
    );
  }

  return (
    <section className="flex flex-col gap-5 rounded-2xl border border-[#d2e0f5] bg-white/95 p-6 sm:p-8 shadow-sm backdrop-blur-sm" aria-label={heading}>
      {/* Top Header */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="size-2 bg-[#155ff2]" />
            <span className="font-label text-xs font-bold tracking-[0.2em] text-[#155ff2] uppercase">
              AI RESPONSE
            </span>
          </div>
          <span className="hidden sm:inline font-label text-[10px] font-bold tracking-[0.2em] text-[#6b82a6] uppercase">
            KNOWLEDGE TODAY // A BRIGHTER TOMORROW
          </span>
        </div>

        <div>
          <div className="flex flex-wrap items-center gap-3">
            <span className="inline-block w-1.5 h-8 bg-[#00d4ff] rounded-full mr-1 shrink-0" />
            <h1 className="copie-heading font-display text-3xl sm:text-4xl font-black italic tracking-tight text-[#080b12]">
              {heading}
            </h1>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-[#155ff2]/30 bg-blue-50 px-3 py-1 text-xs font-semibold text-[#155ff2]">
              <span className="size-1.5 rounded-full bg-[#155ff2]" />
              ข้อมูลตัวอย่างสำหรับออกแบบ
            </span>
          </div>

          <div className="text-sm font-medium text-[#6b82a6] mt-2 leading-relaxed">
            <p>ต่อไปนี้เป็นตัวอย่างรายวิชาของปี {data.year} เทอม {data.semester} เพื่อใช้สำหรับการออกแบบหน้าจอเท่านั้น</p>
            <p>รายวิชาและหน่วยกิตอาจแตกต่างกันตามหลักสูตรและสถาบันการศึกษา โปรดตรวจสอบข้อมูลจากคณะ/มหาวิทยาลัยของคุณอีกครั้ง</p>
          </div>
        </div>
      </div>

      {/* Desktop Table */}
      <div className="hidden md:block overflow-x-auto rounded-xl border border-[#d2e0f5] bg-white shadow-xs">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="bg-slate-50/80 border-b border-[#d2e0f5]">
              {COLUMNS.map((column) => (
                <th
                  key={column.key}
                  scope="col"
                  className={`px-5 py-3.5 font-display text-sm font-bold text-[#080b12] ${
                    column.align === "right" ? "text-right" : "text-left"
                  }`}
                >
                  <button
                    type="button"
                    onClick={() => toggleSort(column.key)}
                    disabled={disabled}
                    className="inline-flex items-center gap-1 rounded cursor-pointer disabled:opacity-50"
                  >
                    {column.label}
                    <ChevronDown
                      aria-hidden="true"
                      className={`size-3.5 transition-transform ${
                        sort?.key === column.key ? "text-[#155ff2]" : "text-[#6b82a6]"
                      } ${sort?.key === column.key && sort.direction === "desc" ? "rotate-180" : ""}`}
                    />
                  </button>
                </th>
              ))}
              <th scope="col" className="w-10 px-3 py-3.5">
                <span className="sr-only">ดูรายละเอียด</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {courses.map((course, index) => {
              const active = course.code === selected;
              return (
                <motion.tr
                  key={course.code}
                  initial={animate ? { opacity: 0, y: 6 } : false}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: animate ? index * 0.04 : 0 }}
                  onClick={() => toggleRow(course.code)}
                  data-selected={active}
                  className={`cursor-pointer border-t border-[#d2e0f5]/60 transition-all ${
                    active
                      ? "bg-blue-50/70 border-[#155ff2] shadow-xs"
                      : "hover:bg-slate-50/60"
                  }`}
                >
                  <td className="relative whitespace-nowrap px-5 py-3.5 font-bold tabular-nums text-[#080b12]">
                    {active && <span aria-hidden="true" className="absolute inset-y-0 left-0 w-1.5 bg-[#00d4ff]" />}
                    <span className={active ? "text-[#155ff2]" : ""}>{course.code}</span>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className={`block font-semibold ${active ? "text-[#155ff2]" : "text-[#080b12]"}`}>
                      {course.name_th}
                    </span>
                    {course.name_en && (
                      <span className="block text-xs text-[#6b82a6]">{course.name_en}</span>
                    )}
                  </td>
                  <td className="px-5 py-3.5 text-right font-display font-bold tabular-nums text-[#080b12]">
                    {course.credits}
                  </td>
                  <td className="px-5 py-3.5 text-sm font-medium text-[#080b12]/80">
                    {course.category ?? "—"}
                  </td>
                  <td className="px-3 py-3.5 text-right">
                    <ChevronRight
                      aria-hidden="true"
                      className={`inline size-4.5 transition-transform ${
                        active ? "text-[#155ff2]" : "text-[#6b82a6]"
                      }`}
                    />
                  </td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Mobile Cards */}
      <ul className="flex flex-col gap-2.5 md:hidden">
        {courses.map((course, index) => {
          const active = course.code === selected;
          return (
            <motion.li
              key={course.code}
              initial={animate ? { opacity: 0, y: 6 } : false}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: animate ? index * 0.04 : 0 }}
            >
              <button
                type="button"
                onClick={() => toggleRow(course.code)}
                aria-expanded={active}
                className={`flex w-full flex-col gap-1 rounded-xl border p-4 text-left transition-all ${
                  active ? "border-[#155ff2] bg-blue-50/70 shadow-xs" : "border-[#d2e0f5] bg-white"
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-display font-bold tabular-nums text-[#155ff2]">{course.code}</span>
                  <span className="font-display font-bold tabular-nums text-[#080b12]">{course.credits} หน่วยกิต</span>
                </div>
                <span className="font-semibold text-sm text-[#080b12]">{course.name_th}</span>
                {course.name_en && <span className="text-xs text-[#6b82a6]">{course.name_en}</span>}
                {course.category && <span className="text-xs font-medium text-[#155ff2] mt-1">{course.category}</span>}
              </button>
            </motion.li>
          );
        })}
      </ul>

      {/* Selected Course Detail Box matching Mockup 07 */}
      {selectedCourse && (
        <div className="flex gap-4 rounded-xl border border-[#d2e0f5] bg-white p-5 shadow-xs">
          <div className="flex size-11 items-center justify-center rounded-xl bg-blue-50 text-[#155ff2] shrink-0">
            <FileText className="size-6" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
              <span className="font-display font-bold tabular-nums text-[#155ff2] text-lg">{selectedCourse.code}</span>
              <span className="font-display font-bold text-[#080b12] text-lg">{selectedCourse.name_th}</span>
            </div>
            <p className="mt-2 text-sm leading-relaxed text-[#080b12]/90 font-medium">
              {selectedCourse.description ?? "ศึกษาแนวคิดพื้นฐานของรายวิชา การออกแบบ และการประยุกต์ใช้งานในระบบสารสนเทศและเทคโนโลยีที่เกี่ยวข้อง"}
            </p>
          </div>
        </div>
      )}

      {/* Total Credits Summary Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-[#155ff2]/25 bg-blue-50/60 px-5 py-3.5 shadow-xs">
        <div className="flex items-center gap-3">
          <BarChart3 aria-hidden="true" className="size-5 text-[#155ff2]" />
          <span className="font-display font-bold text-[#080b12] text-base">รวมหน่วยกิตทั้งสิ้น</span>
          <span className="font-display text-3xl font-black italic tabular-nums text-[#155ff2]">
            {data.total_credits}
          </span>
          <span className="font-display font-bold text-[#080b12] text-base">หน่วยกิต</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-[#6b82a6]">
          <span>ที่มา: ข้อมูลตัวอย่างสำหรับออกแบบ</span>
          <Info className="size-3.5 text-[#6b82a6]" />
        </div>
      </div>
    </section>
  );
}

function sortCourses(courses: Course[], key: SortKey, direction: SortDirection): Course[] {
  const factor = direction === "asc" ? 1 : -1;
  return [...courses].sort((a, b) => {
    if (key === "credits") return (a.credits - b.credits) * factor;
    const left = a[key] ?? "";
    const right = b[key] ?? "";
    if (left === right) return 0;
    if (left === "") return 1;
    if (right === "") return -1;
    return left.localeCompare(right, "th") * factor;
  });
}
